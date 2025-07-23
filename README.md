E-commerce AI Data Analytics Agent
A comprehensive AI-powered data analysis system that uses Mistral 7B to answer natural language questions about e-commerce data through SQL queries and interactive visualizations.

🚀 Project Overview
This project creates an intelligent AI agent that can process natural language questions about e-commerce data, convert questions to SQL queries using Mistral 7B LLM, execute queries against a SQLite database, generate interactive visualizations (charts, graphs), provide a web-based dashboard interface and offer real-time API responses.

📋 Prerequisites
System Requirements
Operating System: Windows 10/11, macOS, or Linux

RAM: 16GB minimum (32GB recommended for optimal performance)

Storage: 20GB free space

Python: 3.8 or higher

Required Software
Python 3.8+ - Download from python.org

Ollama - Download from ollama.com

Git (optional) - For cloning the repository

🛠️ Installation Guide
Step 1: Install Python Dependencies
Create a virtual environment (recommended):

bash
python -m venv vamsi
Activate the virtual environment:

bash
# Windows
vamsi\Scripts\activate

# macOS/Linux
source vamsi/bin/activate
Install required packages:

bash
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install pandas==2.1.3
pip install numpy==1.25.2
pip install matplotlib==3.8.2
pip install plotly==5.17.0
pip install streamlit==1.28.2
pip install requests==2.31.0
pip install pydantic==2.5.0
Step 2: Install and Setup Ollama
Download and install Ollama from the official website

Open terminal/command prompt and install Mistral 7B:

bash
ollama pull mistral:7b-instruct
Verify installation:

bash
ollama run mistral:7b-instruct
Type "exit" to close the model after verification.

Step 3: Project Structure
Create your project directory with the following structure:

text
ecommerce_ai_agent/
├── main.py
├── database.py
├── llm_service.py
├── dashboard.py
├── database_setup.py
├── requirements.txt
└── data/
    ├── Product-Level-Total-Sales-and-Metrics-mapped.csv
    ├── Product-Level-Ad-Sales-and-Metrics-mapped.csv
    └── Product-Level-Eligibility-Table-mapped.csv
📁 Project Files
Core Application Files
main.py - FastAPI backend application

database.py - Database management and SQLite operations

llm_service.py - Mistral 7B integration and SQL generation

dashboard.py - Streamlit web dashboard

database_setup.py - Initial database setup and CSV data loading

Data Files
Place your CSV files in the project directory:

Product-Level-Total-Sales-and-Metrics-mapped.csv

Product-Level-Ad-Sales-and-Metrics-mapped.csv

Product-Level-Eligibility-Table-mapped.csv

⚙️ Configuration
Database Setup
Run the database setup script to create and populate the SQLite database:

bash
python database_setup.py
This will:

Create ecommerce_data.db SQLite database

Load your CSV data into three tables: total_sales, ad_sales, eligibility

Verify data integrity

Environment Variables (Optional)
Create a .env file for configuration:

text
DATABASE_PATH=ecommerce_data.db
OLLAMA_BASE_URL=http://localhost:11434
LOG_LEVEL=INFO
🚀 Running the Application
Method 1: Complete Setup (Recommended)
Start Ollama service (if not running):

bash
ollama serve
Start the FastAPI backend:

bash
python main.py
The API will be available at http://localhost:8000

Start the Streamlit dashboard (new terminal):

bash
streamlit run dashboard.py
The dashboard will be available at http://localhost:8501

Method 2: Individual Components
Start each component separately for development:

Backend only:

bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Dashboard only:

bash
streamlit run dashboard.py
📊 API Usage
Demo Endpoints
Test the three main demo questions:


🎨 Dashboard Features
The Streamlit dashboard provides:

Interactive Query Interface: Ask questions in natural language

Pre-built Demo Questions: Quick access to common queries

Real-time Visualizations: Charts and graphs based on query results

SQL Query Display: View generated SQL for transparency

Database Schema Explorer: Browse table structures

Multiple Chart Types: Bar charts, line charts, pie charts, scatter plots


📦 Dependencies
Core Dependencies
text
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.25.2
streamlit==1.28.2
requests==2.31.0
pydantic==2.5.0
Visualization Dependencies
text
matplotlib==3.8.2
plotly==5.17.0
Optional Dependencies
text
python-dotenv==1.0.0  # For environment variables
pytest==7.4.3         # For testing
black==23.9.1          # Code formatting

Ensure Ollama and Mistral 7B are properly set up

Check that your CSV data files are in the correct format

For additional support, ensure your system meets the minimum requirements and all installation steps have been followed correctly.
