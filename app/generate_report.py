from models import product
import sys

sys.path.insert(1, '../')

def execute_job():
    try:
        productObj = product.Product()
        productObj.generate_report()
    except Exception as e:
        print(e)
