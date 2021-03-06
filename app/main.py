from fastapi import FastAPI, File, UploadFile, Request, Form, Depends
from fastapi.templating import Jinja2Templates
import aiofiles
import asyncio
from typing import List, Optional, Callable, Any, Iterator
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session, sessionmaker
# from utils.data_ingestion import save_upload_file_tmp
from strgen import StringGenerator as SG
from timeit import default_timer as timer

import models
from utils import data_ingestion, hashing
from models import product
import os

models.create_database() # creating postman database
#models.create_airflow_role()

partition_factor = os.environ.get('PARTITION_FACTOR')
print(partition_factor)
partitionObj = hashing.PartitionCode(partition_factor)
partition_count = partitionObj.get_partition_count()
print(partition_count)

product_db = product.Product()
product_db.create_table()
product_db.create_report_table()
product_db.create_partition(partition_count=partition_count)

app = FastAPI()

try:
    templates = Jinja2Templates(directory='templates')
except :
    print("Template Error!")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    filename = SG(r"[\w]{30}").render()
    start = timer()
    async with aiofiles.open(f'./temp/{filename}.csv', 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    end = timer()
    print(f"[INFO] [I/O OPS] took time {end - start} seconds.")
    # temp_file = _save_file_to_disk(file, path='temp', save_as='temp')
    start = timer()
    # print("Started Ingestion")
    ingestion_resp = data_ingestion.ingest_data(f'./temp/{filename}.csv')
    # print("Complete Ingestion")
    end = timer()
    os.remove(f'./temp/{filename}.csv')
    if ingestion_resp:
        return {"status": "OK","message":f"Data Ingested with {end - start} seconds :)"}
    else:
        return {"status": "ALERT","message":"Uploaded but Data Ingestion Terminated :/"}


# sqlalchemy setup for pagination
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postman")
SessionLocal = sessionmaker(autocommit=True, autoflush=True, bind=engine)
Base = declarative_base(bind=engine)

class Report(Base):
    __tablename__ = 'product_report'
    __table_args__ = {'extend_existing': True}
    name = Column('name', String, primary_key = True)
    no_of_products = Column("no. of products", Integer)

class ReportOut(BaseModel):
    name : str
    no_of_products : int

    class Config:
        orm_mode = True

def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/report', response_model = Page[ReportOut])
def get_users(db: Session = Depends(get_db)) -> Any:
    return paginate(db.query(Report))

add_pagination(app)

    # try:
    #     obj = models.ConnectDB().initialise()
    #     with obj.cursor() as cursor:
    #         cursor.execute("""SELECT * FROM product_report""")
    #         obj.commit()
    #     obj.terminate()
    #     return {"status":"OK", "data":product.generate_report()}
    # except Exception as e:
    #     return {"status": "ALERT","message":"Still Working on it"}




# @app.post("/uploadfile/")
# def handle_upload_file(upload_file: UploadFile, handler: Callable[[Path], None]) -> None:
#     tmp_path = save_upload_file_tmp(upload_file)
#     try:
#         handler(tmp_path)  # Do something with the saved temp file
#     finally:
#         tmp_path.unlink()  # Delete the temp file

#     return {"status": "OK","message":"Data Ingested :)"}