# postman-assignment

#### Execution

> ./start_script.sh

Containerisation is not successful yet due to
1. Public Issue in Airflow official Docker Image
2. Used ***puckel/docker-airflow*** for airflow service
3. ***aggregated table*** is implemented by airflow job scheduler [NOT Completed Since bug exists]
4. Multiple Data Ingestion possible - FastAPI server hosted with Browser UI

#### Execution on local device
1. Install dependencies using pip [Python 3.8 recommended]
2. run ***uvicorn main:app --reload***
3. Open **http://127.0.0.1:8000**

