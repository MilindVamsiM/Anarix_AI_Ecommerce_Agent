from database import DatabaseManager

def test_database():
    """Test the database connection and display sample data"""
    db = DatabaseManager("ecommerce_data.db")
    
    print("🧪 Testing Database Connection...")
    
    if db.test_connection():
        print("\n📊 Database Schema:")
        schema = db.get_schema_info()
        for table, columns in schema.items():
            print(f"  📋 {table}: {columns}")
        
        print("\n🔍 Testing Demo Queries:")
        
        # Test total sales
        try:
            result = db.execute_query("SELECT SUM(total_sales) as total_sales FROM total_sales;")
            total_sales = result['total_sales'].iloc[0]
            print(f"  💰 Total Sales: ${total_sales:,.2f}")
        except Exception as e:
            print(f"  ❌ Total Sales Error: {e}")
        
        # Test RoAS
        try:
            result = db.execute_query("""
                SELECT ROUND(SUM(ad_sales) / SUM(ad_spend), 2) as roas 
                FROM ad_sales WHERE ad_spend > 0;
            """)
            roas = result['roas'].iloc[0]
            print(f"  📈 RoAS: {roas}")
        except Exception as e:
            print(f"  ❌ RoAS Error: {e}")
        
        # Test highest CPC
        try:
            result = db.execute_query("""
                SELECT item_id, ROUND(SUM(ad_spend) / SUM(clicks), 2) as cpc
                FROM ad_sales WHERE clicks > 0 
                GROUP BY item_id ORDER BY cpc DESC LIMIT 1;
            """)
            item_id = result['item_id'].iloc[0]
            cpc = result['cpc'].iloc[0]
            print(f"  🎯 Highest CPC: Product {item_id} - ${cpc}")
        except Exception as e:
            print(f"  ❌ Highest CPC Error: {e}")
    
    else:
        print("❌ Database connection failed!")

if __name__ == "__main__":
    test_database()
