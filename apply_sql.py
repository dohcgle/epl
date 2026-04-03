import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def apply_sql():
    sql_file = 'document_processor/sql/save_loan_application.sql'
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    with connection.cursor() as cursor:
        cursor.execute(sql)
        print("SQL applied successfully.")

if __name__ == '__main__':
    apply_sql()
