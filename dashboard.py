import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Page config
st.set_page_config(
    page_title="E-commerce AI Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# App title
st.title("🛍️ E-commerce AI Analytics Dashboard")
st.markdown("Ask questions about your e-commerce data using natural language!")

# Sidebar
st.sidebar.header("🎮 Controls")
api_base_url = st.sidebar.text_input("API Base URL", "http://localhost:8000")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Ask Your Question")
    
    # Predefined questions
    st.subheader("📋 Quick Questions")
    demo_questions = [
        "What is my total sales?",
        "Calculate the RoAS (Return on Ad Spend)",
        "Which product had the highest CPC (Cost Per Click)?",
        "Show total sales by product for top 10 products",
        "Show sales trend over time",
        "Show distribution of ad spend vs ad sales"
    ]
    
    # Display demo question buttons
    cols = st.columns(3)
    for i, question in enumerate(demo_questions):
        col_idx = i % 3
        with cols[col_idx]:
            if st.button(question, key=f"demo_{i}"):
                st.session_state.selected_question = question

    # Custom question input
    st.subheader("✍️ Custom Question")
    custom_question = st.text_input("Enter your question:", placeholder="e.g., Show me sales by product category")
    
    # Chart option
    include_chart = st.checkbox("📈 Include Chart", value=True)
    
    # Process question
    question_to_process = None
    
    if st.button("🚀 Ask Question") and custom_question:
        question_to_process = custom_question
    elif hasattr(st.session_state, 'selected_question'):
        question_to_process = st.session_state.selected_question
        delattr(st.session_state, 'selected_question')

with col2:
    st.header("📊 Database Schema")
    
    if st.button("🔄 Load Schema"):
        try:
            response = requests.get(f"{api_base_url}/schema")
            if response.status_code == 200:
                schema = response.json()["schema"]
                for table, columns in schema.items():
                    st.subheader(f"📋 {table}")
                    st.write(", ".join(columns))
        except Exception as e:
            st.error(f"Error loading schema: {e}")

# Process and display results
if question_to_process:
    st.header("🎯 Results")
    
    with st.spinner("🤖 AI is processing your question..."):
        try:
            # Make API call
            payload = {
                "question": question_to_process,
                "include_chart": include_chart
            }
            
            response = requests.post(f"{api_base_url}/ask", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display results in two columns
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.success("✅ Question processed successfully!")
                    
                    # Display the formatted answer prominently
                    st.subheader("💡 Answer")
                    st.markdown(f"**{result['formatted_response']}**")
                    
                    # Display SQL query
                    with st.expander("🔍 View SQL Query"):
                        st.code(result["sql_query"], language="sql")
                    
                    # Display raw data
                    with st.expander("📋 View Raw Data"):
                        if result["result"]:
                            try:
                                data_dict = json.loads(result["result"])
                                df = pd.DataFrame(data_dict)
                                st.dataframe(df, use_container_width=True)
                            except:
                                st.text(result["result"])
                
                with col2:
                    # Display chart if available
                    if result.get("chart_data"):
                        st.subheader("📊 Visualization")
                        try:
                            chart_json = json.loads(result["chart_data"])
                            st.plotly_chart(chart_json, use_container_width=True)
                            
                            # Show chart type
                            if result.get("chart_type"):
                                st.caption(f"Chart Type: {result['chart_type'].title()}")
                                
                        except Exception as e:
                            st.error(f"Error displaying chart: {e}")
                    else:
                        st.info("No visualization generated for this query")
            
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            st.error(f"❌ Connection error: {e}")

# Footer
st.markdown("---")
st.markdown("🚀 **E-commerce AI Analytics Dashboard** - Powered by Mistral 7B & FastAPI")
