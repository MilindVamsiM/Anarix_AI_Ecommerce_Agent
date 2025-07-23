import requests
import json
import re

class MistralLLMService:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral:7b-instruct"
    
    def generate_sql_query(self, question, schema_info):
        """Generate SQL query from natural language question"""
        schema_text = self._format_schema(schema_info)
        
        prompt = f"""
You are an expert SQL analyst. Given the database schema below, convert the natural language question into a precise SQL query.

Database Schema:
{schema_text}

Important Table Information:
- ad_sales: Contains advertising sales data with columns like date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold
- total_sales: Contains total sales data with columns like date, item_id, total_sales, total_units_ordered  
- eligibility: Contains product eligibility data with columns like eligibility_datetime_utc, item_id, eligibility, message

CRITICAL RULES FOR SPECIFIC QUERIES:
1. For "highest CPC" or "maximum CPC": Use ORDER BY cpc DESC LIMIT 1
2. For "lowest CPC" or "minimum CPC": Use ORDER BY cpc ASC LIMIT 1
3. For "highest RoAS": Use ORDER BY roas DESC LIMIT 1
4. For "lowest RoAS": Use ORDER BY roas ASC LIMIT 1

IMPORTANT RULES:
1. Return ONLY the SQL query, no explanations, no "SQL" prefix, no markdown
2. Start directly with SELECT, INSERT, UPDATE, or DELETE
3. Use proper SQLite syntax
4. For RoAS calculations: SUM(ad_sales) / SUM(ad_spend) WHERE ad_spend > 0
5. For CPC calculations: SUM(ad_spend) / SUM(clicks) WHERE clicks > 0
6. For total sales: SUM(total_sales) FROM total_sales
7. Use ROUND() with 2 decimal places for financial calculations
8. End with a single semicolon
9. Filter out zero denominators with WHERE clauses
10. Do not generate multiple statements or fragments

Special calculation rules:
    - For RoAS (Return on Ad Spend): Use SUM(ad_sales) / SUM(ad_spend)
    - Always filter WHERE ad_spend > 0 for RoAS calculations
    - Use ROUND() function with 2 decimal places for financial calculations

Question: {question}

Query:"""

        response = self._call_ollama(prompt)
        sql_query = self._extract_sql_from_response(response)
        return sql_query
    
    def format_response(self, question, query_result, original_question):
        """Format the query result into a human-readable response"""
        prompt = f"""
You are a business analyst. Format the following query result into a clear, professional response.

Original Question: {original_question}
Query Result: {query_result}

Provide a concise, business-friendly answer that directly addresses the question. Include specific numbers and insights.

Response:"""

        response = self._call_ollama(prompt)
        return response.strip()
    
    def _call_ollama(self, prompt):
        """Make API call to Ollama with clean logging"""
        try:
            print("Making API call to Ollama...")
            print(f"URL: {self.base_url}/api/generate")
            print(f"Model: {self.model}")
            print(f"Prompt length: {len(prompt)} characters")
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            print("Sending request to Mistral 7B...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                llm_response = response.json()["response"]
                print("LLM Response received!")
                print(f"Response length: {len(llm_response)} characters")
                print(f"LLM Output: {llm_response[:200]}..." if len(llm_response) > 200 else f"LLM Output: {llm_response}")
                return llm_response
            else:
                print(f"LLM API Error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            print(f"LLM Service Error: {str(e)}")
            return f"Error calling LLM: {str(e)}"
    
    def _format_schema(self, schema_info):
        """Format schema information for the prompt"""
        schema_text = ""
        for table, columns in schema_info.items():
            schema_text += f"\nTable: {table}\nColumns: {', '.join(columns)}\n"
        return schema_text
    
    def _extract_sql_from_response(self, response):
        """Extract SQL query from LLM response"""
        # Remove markdown code blocks
        response = response.replace('``````', '')
        
        # Remove common prefixes
        prefixes_to_remove = ['SQL:', 'Query:', 'Answer:', 'SQL ', 'Query ', 'Answer ']
        for prefix in prefixes_to_remove:
            if response.strip().upper().startswith(prefix.upper()):
                response = response.strip()[len(prefix):].strip()
        
        # Clean up the response line by line
        lines = response.strip().split('\n')
        sql_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#') and not line.startswith('--') and not line.startswith('/*'):
                # Remove any remaining prefixes from individual lines
                line_upper = line.upper()
                if line_upper.startswith('SQL '):
                    line = line[4:].strip()
                sql_lines.append(line)
        
        # Join all SQL lines
        sql_query = ' '.join(sql_lines).strip()
        
        # Clean up multiple semicolons
        while ';;' in sql_query:
            sql_query = sql_query.replace(';;', ';')
        
        # Ensure query ends with single semicolon
        sql_query = sql_query.rstrip(';')
        if sql_query:
            sql_query += ';'
        
        return sql_query
