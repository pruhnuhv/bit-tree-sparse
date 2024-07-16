import json
import math
from collections import OrderedDict
import sys
import numpy as np
import time
from DRAM import DRAM
from ZDU import ZDU
from Cache import Cache
from PE import PE


class simMatMul:
    def __init__(self, hardware_configfile):

        self.config = hardware_configfile
        self.clock_freq = self.config["frequency"]
        self.DRAM = DRAM(self.config, metadata=False)
        self.DRAMmetadata = DRAM(self.config, metadata=True)
        self.stabuf = Cache(self.config)
        self.stabuf_metadata = Cache(self.config, metadata=True)
        self.strbuf = Cache(self.config)
        self.strbuf_metadata = Cache(self.config, metadata=True)
        self.PE = PE(self.config)
        self.pe_count = self.config["pe_count"]
        self.bit_width = self.config["bit_width"]
        self.run_cycles = 0
        self.stalls = 0
        self.run_ms = 0
        self.str_tilesize = self.config["str_tilesize"]
        self.strPII = self.config["strPII"] #Streaming Parallelism (no. of FIFOS/Stream Regs in Parallel)
        self.add_lat = self.config["add_lat"]
        self.mult_lat = self.config["mult_lat"]
        self.leaf_size = self.config["leaf_size"]
        self.dissimilarity = self.config["StaDissimilarity"]
        self.nLeafAcc = int(self.str_tilesize/self.leaf_size)
        self.accInLeaf = int(self.leaf_size/2)    
            
    def run(self, matrixA, bitmaskA, matrixB, bitreeB, bitmaskB):

        # ''' Continuous Read of A row NZ's directly from DRAM to stabuf'''
        assert len(matrixA) == len(bitmaskA)
        assert len(bitreeB) == len(matrixB) == len(bitmaskB)
        assert len(matrixB[0]) == len(bitmaskB[0]) == self.leaf_size*len(bitreeB[0])
        assert(self.strPII == self.accInLeaf * self.nLeafAcc) #Producer-Consumer Balance

        nBchunks = int(math.ceil(len(matrixB[0])/self.str_tilesize))
        PEcycles_row_chunk = []
        rowid = 0
        stall_cycles = 0
        zchunk = 0
        for row, bitvArow in zip(matrixA, bitmaskA):
            if (bitvArow.count(1) == 0):
                rowid += 1
                PEcycles_row_chunk.append([[] for i in range(nBchunks)])
                continue
            stall_cyclesRow, chunkcycles = self.PE.MatMulChunks(row, bitvArow, matrixB, bitreeB, bitmaskB, rowid) 
            if(chunkcycles) == 0:
                assert(False)
            PEcycles_row_chunk.append(chunkcycles)
            rowid += 1
            stall_cycles += int(math.ceil(stall_cyclesRow/self.strPII))
        assert len(PEcycles_row_chunk[5]) == nBchunks 
        # print(stall_cycles) 
        sparsevals = []
        for row in matrixA:
            temp = [i for i in row if i != 0]        
            sparsevals.append(temp)
            #print(f"NNZ A row: {len(temp)}")
        total_cyc = 0
        total_lat = 0
        rowid = 0
        for row, bitvArow in zip(sparsevals, bitmaskA):
        
        
            # '''Empty Stationary Row => Empty Output Row'''
            if (bitvArow.count(1) == 0):
                rowid += 1
                continue
           
            #TODO: Currently taking a worst case execution for streaming stalls. Incur mem access overhead. Can be optimized for better performance
            # '''Latency to load stationary row'''
            stalat, staCyc = self.DRAM.read(row)
            stalat_m, staCyc_m = self.DRAMmetadata.read(bitvArow)

            stalat_2, staCyc_2 = self.stabuf.read(row)
            stalat_m_2, staCyc_m_2 = self.stabuf_metadata.read(bitvArow)
        
            staRead_latency = max (stalat, stalat_m) + max (stalat_2, stalat_m_2)
            staRead_cycles = max (staCyc, staCyc_m, staCyc_2, staCyc_m_2)
           
            sta_row_compute_latency = 0
            sta_row_compute_cycles = 0
            
            # ''' Worst case Latency to fill Streaming Chunks'''
            nvals = self.str_tilesize*100
            strtemp = [1 for i in range(nvals)]
            strtempMetadata = [1 for i in range(nvals)] 
            strlat, strCyc = self.DRAM.read(strtemp)
            strlat_m, strCyc_m = self.DRAMmetadata.read(strtempMetadata)
             
            strlat_2, strCyc_2 = self.strbuf.write(strtemp)
            strlat_m_2, strCyc_m_2 = self.strbuf_metadata.write(strtempMetadata)
             
            strRead_latency = max (strlat, strlat_m, strlat_2, strlat_m_2)
            strRead_cycles = max (strCyc, strCyc_m, strCyc_2, strCyc_m_2)
            
            wblat, wbCyc = self.DRAM.write([1 for i in range(bitvArow.count(1))])
            wblat_m, wbCyc_m = self.DRAMmetadata.write(bitvArow)
            sta_row_compute_latency = self.add_lat + self.mult_lat 
            output_writeback_latency = max(wblat, wblat_m)
            stall_cycles_row = 0 
           
            # '''Compute on B chunks'''
            for i in range(nBchunks):
                # ''' l new rows to stream in for processing '''
                newReadRows = [1 for i in range(self.str_tilesize*self.dissimilarity)]
                newReadLat, newReadCyc = self.DRAM.read(newReadRows) 
                chunk_compute_cycles = sum(PEcycles_row_chunk[rowid][i]) 
                stall_cycles_sta_row = max(newReadCyc, chunk_compute_cycles, wbCyc, wbCyc_m) - chunk_compute_cycles
                sta_row_compute_cycles += chunk_compute_cycles  
           
            if stall_cycles_sta_row > 0:
                stall_cycles += stall_cycles_sta_row 
            rowid += 1
            total_cyc += max(sta_row_compute_cycles, staRead_cycles)
        
        total_lat = (sta_row_compute_latency + max(strRead_latency, staRead_latency, output_writeback_latency))*nBchunks
        stall_cycles = int(math.ceil(stall_cycles/(self.pe_count-2)))
        total_cyc = int(math.ceil(total_cyc/self.pe_count)) 
        self.stall_cycles = stall_cycles
        self.run_cycles += total_lat + total_cyc + stall_cycles
        self.run_ms = ( self.run_cycles / (self.clock_freq * 1e3))
        return 0


    def reset(self):
        self.stabuf.reset()
        self.strbuf.reset()
        self.stabuf_metadata.reset()
        self.strbuf_metadata.reset()
        self.DRAMmetadata.reset()
        self.run_cycles = 0
        self.run_ms = 0
        self.stall_cycles = 0
        return 0
