import mysql.connector
from mysql.connector import Error
import pandas as pd

# Function to upload CSV data to MySQL
def upload_csv_to_mysql(file_path, table_name, db_params):
    connection = mysql.connector.connect(**db_params)
    cursor = connection.cursor()
    df = pd.read_csv(file_path)
    df.to_sql(table_name, connection, if_exists='replace', index=False)
    connection.commit()
    print(f"Data from {file_path} uploaded to {table_name} successfully.")
    cursor.close()

# Function to execute a stored procedure
def call_stored_procedure(connection, table_name):
    try:
        cursor = connection.cursor()
        cursor.callproc('GetTableInfo', [table_name])
        for result in cursor.stored_results():
            print(f"Result from query: {result.statement}")
            rows = result.fetchall()
            for row in rows:
                print(row)
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Function to create a view by joining two tables
def create_view(connection):
    try:
        cursor = connection.cursor()
        create_view_query = """
        CREATE OR REPLACE VIEW Expected_Actual_Cashflow_View AS
        SELECT 
            ec.`Premiums`,
            ac.`Claims`
        FROM 
            Expected_Cashflow_Statement ec
        JOIN 
            Actual_Cashflow_Statement ac ON ec.`Renewal Commission` = ac.`Renewal Commission`;
        """
        cursor.execute(create_view_query)
        connection.commit()
        print("View 'Expected_Actual_Cashflow_View' created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Function to execute CTE and window functions
def execute_cte_and_window_function(connection):
    try:
        cursor = connection.cursor()
        cte_query = """
        WITH MonthlyPremiums AS (
            SELECT 
                ContractID, 
                SUM(Premium) AS TotalPremium, 
                MONTH(Date) AS Month
            FROM 
                insurance_data
            GROUP BY 
                ContractID, MONTH(Date)
        )
        SELECT 
            ContractID, 
            TotalPremium, 
            SUM(TotalPremium) OVER (PARTITION BY ContractID ORDER BY Month) AS CumulativePremium
        FROM 
            MonthlyPremiums;
        """
        cursor.execute(cte_query)
        for result in cursor.fetchall():
            print(result)
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

# Main Execution
if __name__ == "__main__":
    db_params = {
        'host': 'localhost',
        'user': 'your_username',
        'password': 'your_password',
        'database': 'your_database'
    }
    
    csv_files = {
        'insurance_data.csv': 'insurance_data'
    }

    try:
        connection = mysql.connector.connect(**db_params)
        if connection.is_connected():
            print("Connected to MySQL database")

            for file_path, table_name in csv_files.items():
                upload_csv_to_mysql(file_path, table_name, db_params)
            print("All CSV files have been uploaded to MySQL.")

            call_stored_procedure(connection, 'Expected_Cashflow_Statement')
            create_view(connection)
            print("View created")
            execute_cte_and_window_function(connection)
            print("CTE executed")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            connection.close()
            print("MySQL connection is closed")
