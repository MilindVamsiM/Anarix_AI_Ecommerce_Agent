# E-commerce AI Data Analytics Agent

An AI-powered FastAPI and Streamlit solution that answers natural language queries about your e-commerce business with metrics, insights, and automatic visualizations, using Mistral 7B or compatible LLMs.

Your project loads e-commerce sales, ad sales, and eligibility data from CSVs into a SQLite database, enabling both programmatic (API) and interactive (dashboard) access.

## 🚀 Features

- **FastAPI Backend** - RESTful API for programmatic data querying and insight generation
- **Streamlit Dashboard** - Interactive web interface for business intelligence queries
- **AI-Powered Analytics** - Automatic SQL query generation via Mistral 7B model (via Ollama)
- **Smart Formatting** - LLM-powered business-friendly explanations and insights
- **Automatic Visualizations** - Dynamic chart generation (bar, line, pie charts, etc.)
- **Demo Endpoints** - Pre-built KPI queries (Total Sales, RoAS, Highest CPC, etc.)

## 📁 Project Structure

```
ecommerce-ai-analytics/
│
├── main.py              # FastAPI application
├── dashboard.py         # Streamlit dashboard UI
├── database.py          # SQLite connections and database logic
├── llm_service.py       # LLM integration (Ollama/Mistral)
├── database_setup.py    # CSV to SQLite data loader
├── requirements.txt     # Python dependencies
├── README.md            # This documentation
└── data/
    ├── Product-Level-Total-Sales-and-Metrics-mapped.csv
    ├── Product-Level-Ad-Sales-and-Metrics-mapped.csv
    └── Product-Level-Eligibility-Table-mapped.csv
```

## 🛠️ Setup & Installation

### Prerequisites

- **Python 3.8+** - [Download from python.org](https://www.python.org/)
- **Ollama** - [Download from ollama.com](https://ollama.com/download)

### 1. Environment Setup

```bash
# Clone or download the project
git clone <your-repository-url>
cd ecommerce-ai-analytics

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies included:**
```
fastapi==0.109.0
uvicorn==0.27.1
pandas
numpy
requests
matplotlib
plotly
streamlit
pydantic
```

### 3. Data Setup

Place your CSV files in the `data/` directory:
- `Product-Level-Total-Sales-and-Metrics-mapped.csv`
- `Product-Level-Ad-Sales-and-Metrics-mapped.csv` 
- `Product-Level-Eligibility-Table-mapped.csv`

Create the SQLite database:
```bash
python database_setup.py
```

This will create `ecommerce_data.db` with three tables: `total_sales`, `ad_sales`, and `eligibility`.

### 4. LLM Setup

Install and configure Ollama with Mistral 7B:

```bash
# Install Ollama (if not already installed)
# Download from: https://ollama.com/download

# Pull Mistral 7B model
ollama pull mistral:7b-instruct

# Start Ollama server
ollama serve
```

Verify Ollama is running at `http://localhost:11434`

## 🚀 Running the Application

### Start the FastAPI Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API Available at:** `http://localhost:8000`  
**API Documentation:** `http://localhost:8000/docs`

### Launch the Streamlit Dashboard

In a new terminal (with activated virtual environment):

```bash
streamlit run dashboard.py
```

**Dashboard Available at:** `http://localhost:8501`

## 💡 Usage Guide

### Interactive Dashboard

Open `http://localhost:8501` and try these sample queries:

**Pre-built Demo Questions:**
- "What is my total sales?"
- "Calculate the RoAS (Return on Ad Spend)"
- "Which product had the highest CPC?"
- "Show total sales by product for top 10 products"
- "Show sales trend over time"

**Custom Queries:**
- Enable "Include Chart" for automatic visualizations
- Ask natural language questions about your business data
- Get AI-powered insights and explanations

### API Usage

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Ask Questions:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is my total sales?", 
    "include_chart": true
  }'
```

**Response Format:**
```json
{
  "question": "What is my total sales?",
  "answer": "Your total sales amount to $1,234,567.89...",
  "chart_data": {...},
  "chart_type": "bar"
}
```

## 📊 Data Schema

### Sales Data (`total_sales`)
- `date` - Transaction date
- `item_id` - Product identifier
- `total_sales` - Revenue amount
- `total_units_ordered` - Quantity sold

### Ad Sales Data (`ad_sales`) 
- `date` - Campaign date
- `item_id` - Product identifier
- `ad_sales` - Ad-driven revenue
- `impressions` - Ad views
- `ad_spend` - Advertising cost
- `clicks` - Ad clicks
- `units_sold` - Units sold via ads

### Eligibility Data (`eligibility`)
- `eligibility_datetime_utc` - Timestamp
- `item_id` - Product identifier
- `eligibility` - Eligibility status
- `message` - Status details

## 🔧 Troubleshooting

### Common Issues

**Unicode Encoding Errors (Windows):**
- Set terminal encoding to UTF-8
- Remove emoji characters from print statements

**Database Connection Issues:**
- Verify CSV files have no blank lines or extra columns
- Delete `ecommerce_data.db` and re-run `database_setup.py`

**LLM Not Responding:**
- Ensure Ollama is running: `ollama serve`
- Verify Mistral model is available: `ollama list`
- Check connectivity to `http://localhost:11434`

**Dashboard Not Loading:**
- Confirm both FastAPI and Streamlit are running
- Check for port conflicts (8000, 8501)
- Verify virtual environment is activated

### Performance Tips

- Use Python 3.9+ for optimal performance
- Ensure CSV data is clean and properly formatted
- Monitor system resources when running large queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for APIs
- [Streamlit](https://streamlit.io/) - Interactive web applications
- [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- [Ollama](https://ollama.com/) - Local LLM serving
- [Mistral 7B](https://ollama.com/library/mistral) - Language model

**Built with ❤️ for e-commerce data analytics**  
**Last Updated:** July 23, 2025
