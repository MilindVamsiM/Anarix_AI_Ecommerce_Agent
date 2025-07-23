import sqlite3
import pandas as pd
import os

class DatabaseManager:
    def __init__(self, db_path="ecommerce_data.db"):
        self.db_path = db_path
        
    def execute_query(self, query):
        """Execute SQL query and return results with clean logging"""
        
        print(f"Connecting to SQLite database: {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        
        try:
            print("Executing SQL query...")
            print(f"   Query: {query}")
            
            # Show which table is being accessed
            query_upper = query.upper()
            if 'FROM' in query_upper:
                table_part = query_upper.split('FROM')[1].split()[0]
                print(f"Accessing table: {table_part}")
            
            result = pd.read_sql_query(query, conn)
            
            print("Query successful!")
            print(f"Retrieved {len(result)} rows")
            if not result.empty:
                print(f"Column names: {list(result.columns)}")
                print("First few results:")
                for idx, row in result.head(3).iterrows():
                    print(f"   Row {idx}: {dict(row)}")
            
            return result
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            return f"Error executing query: {str(e)}"
        finally:
            conn.close()
            print("Database connection closed")
    
    def get_schema_info(self):
        """Get database schema information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        schema_info = {}
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            schema_info[table_name] = [col[1] for col in columns]  # Column names
        
        conn.close()
        return schema_info

    def test_connection(self):
        """Test database connection and show sample data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Test each table
            tables = ['ad_sales', 'total_sales', 'eligibility']
            for table in tables:
                try:
                    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
                    print(f"\n{table} table - Sample data:")
                    print(df.head())
                    count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn)
                    print(f"Total rows: {count_df['count'].iloc[0]}")
                except Exception as e:
                    print(f"Error reading {table}: {e}")
            
            conn.close()
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
