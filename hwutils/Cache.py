import math
import logging
logger = logging.getLogger(__name__)

class Cache:
    def __init__(self, config, metadata=False):
        # Cache parameters
        self.latency   = config["cache_latency"]
        self.linesize = config["cache_linesize"]  # elems/cycles per bank
        self.banks = config["cache_banks"]
        self.frequency = config["frequency"] * 1e6
        self.bit_width = config["bit_width"]
        self.bandwidth = int(self.linesize * self.banks * self.bit_width / 8) * self.frequency
        self.metadata = metadata
        self.reads = 0
        self.writes = 0

    def reset(self):
        self.reads = 0
        self.writes = 0
        logging.debug("Cache Reset")

    def read(self, data): 
        read_bytes = len(data) * self.bit_width / 8
        if self.metadata:
            read_bytes = math.ceil(read_bytes/self.bit_width)
        self.reads += int(math.ceil(read_bytes / self.bandwidth))
        start_cycles = self.latency
        read_cycles = int(math.ceil(float(read_bytes / self.bandwidth) * self.frequency))
        logging.debug("Buffer Read, %d Bytes, %d GB/s Bandwidth, %d cycles"%(read_bytes, self.bandwidth/(1e9), read_cycles))
        return start_cycles, read_cycles

    def write(self, data):
        write_bytes = len(data) * self.bit_width / 8
        if self.metadata:
            write_bytes = math.ceil(write_bytes/self.bit_width)
        self.writes += int(math.ceil(write_bytes / self.bandwidth))
        start_cycles = self.latency
        write_cycles = int(math.ceil(float(write_bytes / self.bandwidth) * self.frequency))
        logging.debug("Buffer Write, %d Bytes, %d GB/s Bandwidth, %d cycles"%(write_bytes, self.bandwidth/(1e9), write_cycles))
        return start_cycles, write_cycles
