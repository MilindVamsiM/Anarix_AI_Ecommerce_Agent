from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import io
import base64
import logging
from datetime import datetime
from database import DatabaseManager
from llm_service import MistralLLMService
from typing import Optional

# Configure clean logging without emojis to avoid Unicode errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('demo.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Initialize services globally
db = DatabaseManager("ecommerce_data.db")
llm = MistralLLMService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Starting E-commerce AI Data Agent...")
    
    # Test database connection
    if db.test_connection():
        print("Database connection successful!")
    else:
        print("Database connection failed!")
    
    yield
    print("Application shutting down...")

app = FastAPI(
    title="E-commerce AI Data Agent", 
    version="1.0.0",
    lifespan=lifespan
)

class QueryRequest(BaseModel):
    question: str
    include_chart: bool = False

class QueryResponse(BaseModel):
    question: str
    sql_query: str
    result: str
    formatted_response: str
    chart_data: Optional[str] = None
    chart_type: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "E-commerce AI Data Agent",
        "endpoints": {
            "/ask": "POST - Ask natural language questions",
            "/schema": "GET - View database schema",
            "/health": "GET - Health check",
            "/demo/total-sales": "GET - Demo total sales",
            "/demo/roas": "GET - Demo RoAS calculation",
            "/demo/highest-cpc": "GET - Demo highest CPC",
            "/demo/sample-queries": "GET - Sample visualization queries"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "llm_available": True}

@app.get("/schema")
async def get_schema():
    """Get database schema information"""
    schema = db.get_schema_info()
    return {"schema": schema}

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Process natural language question and return answer with detailed logging"""
    
    # Step 1: Log incoming request
    print("=" * 60)
    print("NEW API REQUEST RECEIVED")
    print(f"Question: '{request.question}'")
    print(f"Include Chart: {request.include_chart}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    try:
        # Step 2: Get database schema
        print("STEP 1: Retrieving database schema...")
        schema_info = db.get_schema_info()
        print("Schema loaded successfully")
        for table, columns in schema_info.items():
            print(f"   Table '{table}': {columns}")
        
        # Step 3: Generate SQL query using LLM
        print("\nSTEP 2: Calling Mistral 7B to generate SQL query...")
        print(f"Sending question to LLM: '{request.question}'")
        
        sql_query = llm.generate_sql_query(request.question, schema_info)
        
        print("SQL Query Generated:")
        print(f"Query: {sql_query}")
        
        # Step 4: Execute query
        print("\nSTEP 3: Executing SQL query against database...")
        print(f"Connecting to database: ecommerce_data.db")
        print(f"Executing: {sql_query}")
        
        query_result = db.execute_query(sql_query)
        
        if isinstance(query_result, pd.DataFrame):
            print(f"Query executed successfully!")
            print(f"Rows returned: {len(query_result)}")
            print(f"Columns: {list(query_result.columns)}")
            print(f"Sample data:")
            print(f"{query_result.head().to_string()}")
            
            # Step 5: Format response using LLM
            print("\nSTEP 4: Formatting response using LLM...")
            formatted_response = llm.format_response(
                request.question, 
                query_result.to_string(), 
                request.question
            )
            print("Response formatted successfully")
            print(f"Final Answer: {formatted_response}")
            
            # Step 6: Generate chart if requested
            chart_data = None
            chart_type = None
            if request.include_chart and not query_result.empty:
                print("\nSTEP 5: Generating chart visualization...")
                chart_data, chart_type = generate_chart(query_result, request.question)
                if chart_data:
                    print(f"Chart generated successfully! Type: {chart_type}")
                else:
                    print("No chart generated (insufficient data)")
            
            # Final response
            print("\nREQUEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
            return QueryResponse(
                question=request.question,
                sql_query=sql_query,
                result=query_result.to_json(),
                formatted_response=formatted_response,
                chart_data=chart_data,
                chart_type=chart_type
            )
        else:
            print(f"Database query failed: {query_result}")
            raise HTTPException(status_code=400, detail=f"Query error: {query_result}")
            
    except Exception as e:
        print(f"ERROR OCCURRED: {str(e)}")
        print("=" * 60)
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

def generate_chart(data, question):
    """Generate appropriate chart based on query results"""
    try:
        if data.empty:
            return None, None
        
        question_lower = question.lower()
        
        # Determine chart type based on question and data
        if len(data.columns) >= 2:
            
            # Time series data (line chart)
            if 'date' in data.columns or any('time' in col.lower() for col in data.columns):
                date_col = 'date' if 'date' in data.columns else [col for col in data.columns if 'time' in col.lower()][0]
                value_col = [col for col in data.columns if col != date_col][0]
                
                fig = px.line(
                    data, 
                    x=date_col, 
                    y=value_col,
                    title=f"Trend Analysis: {question}",
                    markers=True
                )
                return fig.to_json(), "line"
            
            # Sales by product (bar chart)
            elif 'item_id' in data.columns and any('sales' in col.lower() for col in data.columns):
                item_col = 'item_id'
                value_col = [col for col in data.columns if 'sales' in col.lower()][0]
                
                # Limit to top 10 for readability
                top_data = data.nlargest(10, value_col)
                
                fig = px.bar(
                    top_data, 
                    x=item_col, 
                    y=value_col,
                    title=f"Top Products: {question}",
                    text=value_col
                )
                fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                return fig.to_json(), "bar"
            
            # Pie chart for categorical data with percentages
            elif len(data) <= 10 and 'eligibility' in question_lower:
                # For eligibility data
                if 'eligibility' in data.columns:
                    fig = px.pie(
                        data, 
                        names='eligibility', 
                        values=data.columns[1] if len(data.columns) > 1 else 'count',
                        title=f"Distribution: {question}"
                    )
                    return fig.to_json(), "pie"
            
            # Scatter plot for correlation analysis
            elif 'spend' in question_lower and 'sales' in question_lower:
                x_col = [col for col in data.columns if 'spend' in col.lower()][0]
                y_col = [col for col in data.columns if 'sales' in col.lower()][0]
                
                fig = px.scatter(
                    data, 
                    x=x_col, 
                    y=y_col,
                    title=f"Correlation Analysis: {question}",
                    trendline="ols"
                )
                return fig.to_json(), "scatter"
            
            # Default bar chart
            else:
                fig = px.bar(
                    data, 
                    x=data.columns[0], 
                    y=data.columns[1],
                    title=f"Analysis: {question}"
                )
                return fig.to_json(), "bar"
        
        # Single column data (histogram)
        elif len(data.columns) == 1:
            fig = px.histogram(
                data, 
                x=data.columns[0],
                title=f"Distribution: {question}",
                nbins=20
            )
            return fig.to_json(), "histogram"
        
        return None, None
    except Exception as e:
        print(f"Error generating chart: {e}")
        return None, None

# Sample visualization queries endpoint
@app.get("/demo/sample-queries")
async def get_sample_queries():
    """Return sample queries for different visualization types"""
    return {
        "sample_queries": [
            {
                "question": "Show total sales by product for top 10 products",
                "chart_type": "bar",
                "description": "Bar chart showing top performing products"
            },
            {
                "question": "Show sales trend over time",
                "chart_type": "line", 
                "description": "Line chart showing sales progression"
            },
            {
                "question": "Show distribution of ad spend vs ad sales",
                "chart_type": "scatter",
                "description": "Scatter plot showing correlation"
            },
            {
                "question": "Show product eligibility distribution",
                "chart_type": "pie",
                "description": "Pie chart showing eligible vs non-eligible products"
            },
            {
                "question": "Show click distribution across products",
                "chart_type": "histogram",
                "description": "Histogram showing click patterns"
            }
        ]
    }

# Specific endpoints for demo questions
@app.get("/demo/total-sales")
async def get_total_sales():
    """Demo endpoint: What is my total sales?"""
    query = "SELECT SUM(total_sales) as total_sales FROM total_sales;"
    result = db.execute_query(query)
    
    if isinstance(result, pd.DataFrame) and not result.empty:
        total_sales = result['total_sales'].iloc[0]
        return {
            "question": "What is my total sales?",
            "answer": f"Your total sales is ${total_sales:,.2f}",
            "raw_data": float(total_sales),
            "sql_query": query
        }
    else:
        raise HTTPException(status_code=500, detail="Error calculating total sales")

@app.get("/demo/roas")
async def get_roas():
    """Demo endpoint: Calculate the RoAS"""
    query = """
    SELECT 
        SUM(ad_sales) as total_ad_sales,
        SUM(ad_spend) as total_ad_spend,
        ROUND(SUM(ad_sales) / SUM(ad_spend), 2) as roas
    FROM ad_sales 
    WHERE ad_spend > 0;
    """
    result = db.execute_query(query)
    
    if isinstance(result, pd.DataFrame) and not result.empty:
        roas = result['roas'].iloc[0]
        total_ad_sales = result['total_ad_sales'].iloc[0]
        total_ad_spend = result['total_ad_spend'].iloc[0]
        
        return {
            "question": "Calculate the RoAS (Return on Ad Spend)",
            "answer": f"Your Return on Ad Spend (RoAS) is {roas}, meaning you generate ${roas} in sales for every $1 spent on advertising",
            "details": {
                "total_ad_sales": float(total_ad_sales),
                "total_ad_spend": float(total_ad_spend),
                "roas": float(roas)
            },
            "sql_query": query
        }
    else:
        raise HTTPException(status_code=500, detail="Error calculating RoAS")

@app.get("/demo/highest-cpc")
async def get_highest_cpc():
    """Demo endpoint: Which product had the highest CPC?"""
    query = """
    SELECT 
        item_id,
        ROUND(SUM(ad_spend) / SUM(clicks), 2) as cpc
    FROM ad_sales 
    WHERE clicks > 0 
    GROUP BY item_id
    ORDER BY cpc DESC 
    LIMIT 1;
    """
    result = db.execute_query(query)
    
    if isinstance(result, pd.DataFrame) and not result.empty:
        item_id = result['item_id'].iloc[0]
        cpc = result['cpc'].iloc[0]
        
        return {
            "question": "Which product had the highest CPC (Cost Per Click)?",
            "answer": f"Product ID {item_id} had the highest Cost Per Click at ${cpc}",
            "details": {
                "item_id": int(item_id),
                "highest_cpc": float(cpc)
            },
            "sql_query": query
        }
    else:
        raise HTTPException(status_code=500, detail="Error finding highest CPC")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
