import requests
import io
import pandas as pd
import subprocess
import argparse
import sys

AIPROXY_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjEwMDEyOTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.9BoDuWYF8sOQx36Z4T2Y92P7SqKgLXT1K9Vn2DjepiY' 

def parse_args():
    parser = argparse.ArgumentParser(description="Data Analysis Script")
    parser.add_argument('filename', type=str, help='Path to the CSV file')
    return parser.parse_args()
args = parse_args()
    
    # Load the dataset
file_path = args.filename  # Use the filename passed in as an argument 

df = pd.read_csv(file_path)

data_to_feed = df.head(15)  

data_text = data_to_feed.to_string(index=False)

def generate_plan(data_text):
    prompt = f"""
    Here is a portion of a dataset:
    {data_text}
    You are a helpful Data Analysis Guide
    Your role is to act as a key intermediary between raw datasets and the insights they can offer. This requires a strong grasp of the dataset's content and the analytical tools needed to extract valuable information. When presented with a new dataset, your responsibilities include:

    1. Dataset Overview: Offer a detailed description of the dataset, like columns, data types and what type of dataset it is. Ensure that you do not change column names and use them as they are.

    2. Classification of Dataset: Identify what type of category of data, the given dataset falls into. These maybe one of the following or could anyother.
       - Statistical Analysis
       - Machine Learning
       - Data Visualization
       - Natural Language Processing
       - Time Series Analysis
       - Geospatial Analysis
       - Network Analysis
       - Outlier and Anomaly Detection
       - Correlation Analysis, Regression Analysis, and Feature Importance Analysis
       - Cluster Analysis
       - Other (specify additional categories)

    3. Formulation of Research Questions: Based on the dataset overview and classification, generate a series of general research questions that could be explored through data analysis. These questions should be precise, focused, and tied to relevant business or research objectives.

    4. Analysis Plan: For each category of questions, outline a preliminary analysis strategy. This should include the selection of appropriate tools or software in Python such libraries such as Pandas, scikit-learn), methodologies to be used, and hypotheses or expected outcomes.

    5. Data Preparation Guidelines: Provide instructions for preparing the dataset for analysis. This should cover data cleaning, handling missing values, data transformation, and feature engineering techniques based on the questions and analytical methods chosen.

    6. After the data preparation, perform an analysis on the data based on the classification and research questions.

    7. Text-Based Responses: Please provide all answers in text form. Do not include any code.
    """

    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    
    data = {
        "model": "gpt-4o-mini",  
        "messages": [
            {"role": "system", "content": "You are a helpful Data Analysis Manager."},
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.json()}

def generate_code(plan):
    prompt = f"""
    You will be given some information and guidelines. Your role is to do accordingly and write the code in Python for the Data Analysis as prescribed for the research.
    Make sure that all the plots generated are directly saved in directory of the script(code). Also save all the results in a a well labeled dictionary and print that dictionary.
    **Only write the Python code below, without any explanations or extra text.**
    **Do not input in the dataset and use 'df' for the dataframe** 
    {plan}
    """
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    # Define the request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    
    # Define the request data
    data = {
        "model": "gpt-4o-mini",  # Model supported by AI Proxy
        "messages": [
            {"role": "system", "content": "You are a helpful Data Analyst."},
            {"role": "user", "content": prompt}
        ]
    }

    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return (response.json()['choices'][0]['message']['content'])  # Print the response from the proxy
    else:
        # Handle errors if the request fails
        return {"error": f"Request failed with status code {response.status_code}", "details": response.json()}


def run_code(code):
    # Create a string buffer to capture the output
    output = io.StringIO()
    sys.stdout = output  # Redirect stdout to the string buffer

    try:
        exec(code)
    except ImportError as e:
        module = str(e).split()[-1].strip("'")
        print(f"Module {module} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        exec(code)
    
    finally:
        sys.stdout = sys.__stdout__  # Restore original stdout

    # Return the captured output as a string
    return output.getvalue()

def generate_report(plan,code,dictionary):
    prompt = f"""
    You will be given some information and guidelines and the code doing the same and the output of the code in a dictionary. 
    Generate the total analysis report in the form of Readme.md file with descriptive answers. It should also contain the plots stored by the code in the same project folder.
    ***Write only the Readme.md file and nothing more. No extra text**
    Here is the guidelines {plan}\n
    Here is the code used {code}\n
    Here is the results of the code {dictionary}.
    """
     
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    # Define the request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    
    # Define the request data
    data = {
        "model": "gpt-4o-mini",  # Model supported by AI Proxy
        "messages": [
            {"role": "system", "content": "You are a helpful Data Analyst."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return (response.json()['choices'][0]['message']['content'])  # Print the response from the proxy
    else:
        # Handle errors if the request fails
        return {"error": f"Request failed with status code {response.status_code}", "details": response.json()}

plan = generate_plan(data_text)
code = generate_code(plan)
code = code.replace('python', '').strip()
code  = code.replace('```', '').strip()
dictionary = run_code(code)
report = generate_report(plan, code, dictionary)

def main():        
    global report
    with open('README.md', 'w') as file:
        file.write(report)

if __name__ == "__main__":
    main()
