import math
import logging
logger = logging.getLogger(__name__)

class ZDU:
    def __init__(self, config):
        self.stream_slice_len = config["str_tilesize"]
        assert self.stream_slice_len % 4 == 0

    def ZeroDetect_L1(self, bitree_l1):
        firstpass_nz_positions = []
        for (i, val) in enumerate(bitree_l1):
            if val == 1:
                firstpass_nz_positions.append(i)
        return len(firstpass_nz_positions), firstpass_nz_positions

    def ZeroDetect_L2(self, bitree_l2):
        secondpass_nz_positions = []
        leafcount = []
        nz = 0
        if bitree_l2 == []:
            logging.debug("Totally Empty L2 of a Bit-Tree for this row-slice of the chunk\n")
            return 0, []
        #print(bitree_l2)
        for leaf in bitree_l2:
            leaf_nz_positions = []
            for i, val in enumerate(leaf):
                if val == 1:
                    #leaf_nz_positions.append(i%4)
                    leaf_nz_positions.append(i)
                    nz += 1 
            secondpass_nz_positions.append(leaf_nz_positions)    
        leafcount = nz
        return leafcount, secondpass_nz_positions




