import pandas as pd
import sqlite3
import os

def create_database():
    # Your CSV file names (adjust these to match your actual files)
    ad_sales_csv = 'Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped).csv'
    total_sales_csv = 'Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped).csv'
    eligibility_csv = 'Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped).csv'
    
    # Check if files exist
    files = [total_sales_csv, ad_sales_csv, eligibility_csv]
    missing_files = [f for f in files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        print("Make sure these CSV files are in the same directory as this script.")
        return False
    
    try:
        # Create database connection
        conn = sqlite3.connect('ecommerce_data.db')
        
        print("📖 Reading CSV files...")
        
        # Read CSV files
        total_sales_df = pd.read_csv(total_sales_csv)
        ad_sales_df = pd.read_csv(ad_sales_csv) 
        eligibility_df = pd.read_csv(eligibility_csv)
        
        print(f"✅ Total Sales data: {len(total_sales_df)} rows")
        print(f"✅ Ad Sales data: {len(ad_sales_df)} rows")
        print(f"✅ Eligibility data: {len(eligibility_df)} rows")
        
        # Create tables
        print("💾 Creating database tables...")
        total_sales_df.to_sql('total_sales', conn, if_exists='replace', index=False)
        ad_sales_df.to_sql('ad_sales', conn, if_exists='replace', index=False)
        eligibility_df.to_sql('eligibility', conn, if_exists='replace', index=False)
        
        # Verify tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ Database 'ecommerce_data.db' created successfully!")
        print(f"📋 Tables created: {[table[0] for table in tables]}")
        
        # Test sample queries
        print("\n🧪 Testing sample queries...")
        
        # Total sales
        cursor.execute("SELECT SUM(total_sales) as total FROM total_sales;")
        total = cursor.fetchone()[0]
        print(f"  💰 Total Sales: ${total:,.2f}")
        
        # RoAS
        cursor.execute("SELECT SUM(ad_sales)/SUM(ad_spend) as roas FROM ad_sales WHERE ad_spend > 0;")
        roas = cursor.fetchone()[0]
        print(f"  📈 RoAS: {roas:.2f}")
        
        # Highest CPC
        cursor.execute("""
            SELECT item_id, ROUND(SUM(ad_spend)/SUM(clicks), 2) as cpc 
            FROM ad_sales WHERE clicks > 0 
            GROUP BY item_id ORDER BY cpc DESC LIMIT 1;
        """)
        result = cursor.fetchone()
        print(f"  🎯 Highest CPC: Product {result[0]} - ${result[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == '__main__':
    success = create_database()
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("Now you can run: python test_db.py")
    else:
        print("\n💥 Database setup failed!")
