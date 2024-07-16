import math
import logging
logger = logging.getLogger(__name__)

class DRAM:
    def __init__(self, config, metadata=False):
        self.latency   = config["dram_latency"]
        self.bandwidth = config["dram_bandwidth"]
        self.bit_width = config["bit_width"]
        if metadata:
            self.bit_width = 1
        self.bandwidth = self.bandwidth * (2**30)
        self.reads = 0
        self.writes = 0
        self.frequency = config["frequency"]
        self.frequency = self.frequency * 1e6
        assert self.bandwidth % self.bit_width == 0

    def reset(self):
        self.reads = 0
        self.writes = 0
        logging.debug("DRAM Has Been Reset")

    ''' 1D data to be read/written'''
    def read(self, data):
        read_bytes = int(math.ceil(len(data) * self.bit_width/8))
        self.reads += int(math.ceil(read_bytes / self.bandwidth))
        start_cycles = self.latency
        read_cycles = int(math.ceil(float(read_bytes / self.bandwidth) * self.frequency))
        logging.debug("DRAM Read, %d Bytes, %d GB/s Bandwidth, %d Cycles"%(read_bytes, self.bandwidth/(2**30), read_cycles))
        return start_cycles, read_cycles

    def write(self, data):
        write_bytes = int(math.ceil(len(data) * self.bit_width/8))
        self.writes += int(math.ceil(write_bytes / self.bandwidth))
        start_cycles = self.latency
        write_cycles = int(math.ceil(float(write_bytes / self.bandwidth) * self.frequency))
        logging.debug("DRAM Write, %d Bytes, %d GB/s bandwidth, %d Cycles"%(write_bytes, self.bandwidth/(2**30), write_cycles))
        return start_cycles, write_cycles
