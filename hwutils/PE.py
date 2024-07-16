import math
import logging
from ZDU import ZDU
logger = logging.getLogger(__name__)

class PE:
    def __init__(self, config):
        self.config = config
        self.str_tilesize = self.config["str_tilesize"]
        self.ZDU = ZDU(self.config)
        self.strPII = self.config["strPII"]    
        self.banks = self.config["cache_banks"]
        self.cacheline = self.config["cache_linesize"]
        self.leaf_size = self.config["leaf_size"]
        self.nLeafAcc = int(self.str_tilesize/self.leaf_size)
        self.work_steal = int(self.config["work_steal"])
        self.accInLeaf = int(self.leaf_size/2)    

    def __chunkmat(self, matrix, chunk_size):
        # Initialize an empty list to store the chunks
        nchunks = int(math.ceil(len(matrix[0])/chunk_size))
        chunks = [[] for i in range(nchunks)]
        # Loop through the original matrix to create chunks
        for row in matrix:
            cid = 0
            for i in range(0, len(row), chunk_size):
                chunk = row[i:i + chunk_size]  # Extract a row-slice
                chunks[cid].append(chunk)
                cid+=1
        return chunks
    
    def MatMulChunks(self, row, bitvArow, matrixB, bitreeB, bitmaskB, rowid):
       
        stall_cycles = 0
        nnzStaRow = []
        for i, b in enumerate(bitvArow):
            if b and matrixB[i]:
                nnzStaRow.append(i)
        
        '''Fetch all corresponding rows (and their metadata) from the streaming matrix.'''
        str_rows = []
        str_l1 = []
        str_l2 = []
        for rowptr in nnzStaRow:
            str_rows.append(matrixB[rowptr])
            str_l1.append(bitreeB[rowptr])
            str_l2.append(bitmaskB[rowptr])
        assert len(str_l1) == len(nnzStaRow)
        #logging.debug(f"\n\nStationary Row {rowid}: NNZ = {len(str_l1)}")        
        #print(f"\n\nStationary Row {rowid}: NNZ = {len(str_l1)}")        

        '''Streaming Rows tiled into 16 col slices (16 columns corresponding to 4 (x2) leaf accumulators indexing)'''
        l1_chunks =  self.__chunkmat(str_l1, int(self.str_tilesize/self.leaf_size))
        l2_chunks = self.__chunkmat(str_l2, int(self.str_tilesize)) 

        l2_leafs = []
        
        for tile in l2_chunks:
            leafs = []
            for row in tile:
                sublists = [row[i:i+self.leaf_size] for i in range(0, len(row), self.leaf_size)]
                #sublists = [row[i:i + 4] for i in range(0, len(row), 4) if not all(x == 0 for x in row[i:i + 4])]
                leafs.append(sublists)
            l2_leafs.append(leafs)

        '''First Pass NZD on metadata'''
        tilennz_fp = []
        firstpass = []
        for tile in l1_chunks:
            leafnz = []
            leafps = []
            for row in tile:
                tnz, fps = self.ZDU.ZeroDetect_L1(row)
                if tnz:
                    leafnz.append(tnz)
                    leafps.append(fps)
                else:
                    ''' For every completely zero slice, one cycle stall to flush and one to restart'''
                    stall_cycles += 2
            tilennz_fp.append(leafnz)
            firstpass.append(leafps)

        '''Second Pass NZD on metadata'''
        tilennz_sp = []
        secondpass = []
        for tile in l2_leafs:
            rownz = []
            rowleafcounts = []
            for row in tile:
                nnz_row, leafcount = self.ZDU.ZeroDetect_L2(row) 
                if(nnz_row):
                    rownz.append(nnz_row)
                    rowleafcounts.append(leafcount)
            tilennz_sp.append(rownz)
            secondpass.append(rowleafcounts)
        
        '''Simulation of leaf accumulation using the shuffle crossbar'''
        chunkid = 0
        chunkcycles = [[] for i in range(len(firstpass))]
        
        '''Setup cycles for a new chunk'''
        stall_cycles += (int(math.ceil(self.strPII/self.banks)) + self.strPII ) * int(math.ceil(len(bitmaskB[0])/self.str_tilesize))
#        print(f"New Chunk Stalls: {((int(math.ceil(self.strPII/self.banks)) + self.strPII ) * int(math.ceil(len(bitmaskB[0])/self.str_tilesize)))/8}")
         
        for fp, sp in zip(firstpass, secondpass):
            #print(f"Non-zero four leaf vectors (rows) in chunk: {len(fp)}")
            assert len(fp) == len(sp)
            nrows = len(fp)
            
            ''' 
            Number of non-zeroes to be queued per row in a chunk. len(queue) is equal to number of non-zero four
            leaf vectors in that chunk.
            Conditional queuing to accomodate lesser number of leafs in the last chunk after tiling.
            '''
            num_queues = self.nLeafAcc  # You can change this to the desired number of queues
            queues = []
            for i in range(num_queues):
                queue = [(len(sp[j][i])) if len(sp[j]) > i else 0 for j in range(nrows)]
                queues.append(queue)

            ''' Calculate leaf-load for backpressure at each queue for leafAcc '''
            leafs_load = [sum(queue) for queue in queues]
            cycles_list = [int(math.ceil(leaf / self.accInLeaf)) for leaf in leafs_load]
            cycles = 0 
            
            '''Buffer fill for streaming rows on starting a new chunk'''
            #cycles = min(cycles_list) 
            #stall_cycles += (max(cycles_list)*4 - sum(cycles_list))*2 
            if (self.work_steal == 1):
                while cycles_list != []:
                    mincyc = min(cycles_list)
                    cycles_list = [(item-mincyc) for item in cycles_list]
                    maxcyc = max(cycles_list)
                    maxcycid = cycles_list.index(maxcyc)
                    cycles_list[maxcycid] = int(math.ceil(maxcyc/2))
                    if len(cycles_list) != 1:
                        ''' Stall on adders of two leafs for synchronizing after work stealing '''
                        stall_cycles += self.accInLeaf*2
                        cycles_list.remove(0)
                    else:
                        cycles_list.clear()
                    
                    cycles += mincyc
                chunkcycles[chunkid].append(cycles)
                chunkid += 1 
            else:
                maxcyc = max(cycles_list)
                chunkcycles[chunkid].append(maxcyc)
                for raw_cycles in cycles_list:
                    stall_cycles += (maxcyc - raw_cycles)
                chunkid += 1 

        logging.debug(f"Total Cycles for {len(chunkcycles)} chunks of Row {rowid}: {chunkcycles}")
        return int(math.ceil(stall_cycles)), chunkcycles 
