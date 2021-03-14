# app/utils/hasing.py

"""
    Utility module for generate hash code from string,
    which is used for paritioning
"""

import os
class PartitionCode(object):
    def __init__(self, partition_factor=None):
        self.p = 37
        if partition_factor is None or partition_factor < .3:
            self.partition_count = 300
        elif partition_factor > 1:
            self.partition_count = 1000
        else:
            self.partition_count = int(partition_factor * 1000)
            os.environ['PARTITION_COUNT'] = str(self.partition_count)
        

    def get_partition_count(self):
        return self.partition_count

    def get_partition_code(self, key):
        key = str(key)
        current_coefficient = 1
        hash_code = 0
        for character in key:
            hash_code += ord(character) * current_coefficient
            hash_code %= self.partition_count
            current_coefficient *= self.p
            current_coefficient %= self.partition_count
            
        return hash_code % self.partition_count
