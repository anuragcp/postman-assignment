"""
    methods used for data ingestion
"""

from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile
from fastapi import UploadFile
import pandas as pd
from .hashing import PartitionCode
import os
from timeit import default_timer as timer

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from models import product

partition_factor = os.environ.get('PARTITION_FACTOR')
partitionObj = PartitionCode(partition_factor)
partition_count = partitionObj.get_partition_count()


# async def save_upload_file_tmp(upload_file: UploadFile) -> Path:
#     try:
#         suffix = Path(upload_file.filename).suffix
#         with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
#             shutil.copyfileobj(upload_file.file, tmp)
#             tmp_path = Path(tmp.name)
#     finally:
#         upload_file.file.close()
#     return tmp_path

def ingest_data(file_path = None):
    if not file_path:
        return False

    obj = product.Product()

    start = timer()
    for chunk in pd.read_csv(file_path, chunksize=1024, header=0):
        chunk['partition_code'] = chunk['sku'].apply(partitionObj.get_partition_code)
        try:
            for i in range(len(chunk.index)):
                obj.insert_one(chunk.iloc[i].to_list())
        except Exception as e:
            print(e)
            return False

    end = timer()

    print(f"[INFO] [INSERT_DATA] transform and ingestion took {end - start} seconds.")
    
    obj.close_session()
    return True


    
