import requests
import io
import pandas as pd
import subprocess
import argparse
import sys
import traceback
import chardet
import os

# Set up AIPROXY_TOKEN from environment variable
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

# ------------------------------ Helper Function for File input ------------------------------

def parse_args():
    """
    Parse command-line arguments to get the CSV file path.
    """
    parser = argparse.ArgumentParser(description="Data Analysis Script")
    parser.add_argument('filename', type=str, help='Path to the CSV file')
    return parser.parse_args()

def load_data(filename):
    """
    Load a CSV file into a pandas DataFrame, handling various encoding issues.
    
    Args:
    - filename (str): Path to the CSV file.

    Returns:
    - pd.DataFrame: Loaded DataFrame.
    """
    # Try to detect the encoding of the file using chardet
    with open(filename, 'rb') as file:
        raw_data = file.read(10000)  # Read the first 10000 bytes for encoding detection
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    try:
        # Try to read the file using the detected encoding
        df = pd.read_csv(filename, encoding=encoding)
        print(f"File loaded successfully with encoding: {encoding}")
        return df
    except UnicodeDecodeError:
        # If UnicodeDecodeError occurs, try other common encodings
        print(f"Error reading with {encoding}, trying with 'utf-8' encoding.")
        try:
            df = pd.read_csv(filename, encoding='utf-8')
            print("File loaded successfully with 'utf-8' encoding.")
            return df
        except UnicodeDecodeError:
            print("Error reading with 'utf-8', trying with 'ISO-8859-1' encoding.")
            try:
                df = pd.read_csv(filename, encoding='ISO-8859-1')
                print("File loaded successfully with 'ISO-8859-1' encoding.")
                return df
            except UnicodeDecodeError:
                print("Error reading with 'ISO-8859-1', trying with 'latin1' encoding.")
                try:
                    df = pd.read_csv(filename, encoding='latin1')
                    print("File loaded successfully with 'latin1' encoding.")
                    return df
                except Exception as e:
                    # If all encoding attempts fail, raise an error
                    print(f"Error loading file: {e}")
                    raise

# ------------------------------ Helper Function for Sending Request ------------------------------

def send_request(prompt):
    """
    Send a prompt to the OpenAI API to get a response.

    Args:
    - prompt (str): The text prompt to send.

    Returns:
    - dict: Response from the OpenAI API.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AIPROXY_TOKEN}"}
    data = {
        "model": "gpt-4o-mini", 
        "messages": [{"role": "system", "content": "You are a helpful Data Analyst."},
                     {"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.json()}

# ------------------------------ Other Functions ------------------------------

def generate_plan(data_text):
    """
    Generate an analysis plan based on a portion of the dataset.

    Args:
    - data_text (str): A portion of the dataset to analyze.

    Returns:
    - str: A plan for analyzing the dataset.
    """
    prompt = f"""
    Here is a portion of a dataset:
    {data_text}
    You are a helpful Data Analysis Guide
    Your role is to act as a key intermediary between raw datasets and the insights they can offer.
    Please follow these steps:

    1. Dataset Overview: Provide a detailed description of the dataset, including columns and data types.
    2. Classification of Dataset: Identify what type of category of data, the given dataset falls into. These may be one of the following or could be any other:
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
    3. Formulation of Research Questions: Generate research questions based on the dataset.
    4. Analysis Plan: Outline a strategy for each category of questions.
    5. Data Preparation Guidelines: Provide instructions for data cleaning and transformation.
    6. Perform an analysis methodology based on the classification and questions.
    7. Provide text-based responses only (no code).
    """
    return send_request(prompt)

def generate_code(plan):
    """
    Generate Python code based on an analysis plan.

    Args:
    - plan (str): The analysis plan to generate code for.

    Returns:
    - str: Python code to perform the analysis.
    """
    prompt = f"""
    You are a professional coder and a Data Analyst. Write Python code for the Data Analysis based on the following plan, to answer the questions asked.
    The code should save all plots to the script directory and store results in a dictionary.
    **Only write the Python code below, without any explanations or extra text.**
    **Do not input the dataset directly, use 'df' as the dataframe name.**

    {plan}
    """
    return send_request(prompt)

def fix_code(code, error):
    """
    Fix a bug in the code based on the error message.

    Args:
    - code (str): The code to fix.
    - error (str): The error message that needs to be fixed.

    Returns:
    - str: The fixed code.
    """
    prompt = f"""You are a professional debugger. Fix the error in the following code.
    Here is the code: {code}
    Here is the error: {error}
    Rewrite the whole code after fixing the error.
    **Only provide the fixed Python code, no explanations.**"""
    
    return send_request(prompt)

def run_code(code, df):
    """
    Execute the Python code on the provided DataFrame.

    Args:
    - code (str): The code to execute.
    - df (pd.DataFrame): The DataFrame to run the code on.

    Returns:
    - str: The output of the code execution.
    """
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

    return output.getvalue()

def generate_report(plan, code, dictionary):
    """
    Generate a README report based on the analysis plan, code, and results.

    Args:
    - plan (str): The analysis plan.
    - code (str): The generated Python code.
    - dictionary (str): The results from executing the code.

    Returns:
    - str: A generated README report.
    """
    prompt = f"""
    You will be given the analysis Plan, code for the analysis plan and the results from the code when used on the dataset.
    Generate a Readme.md report based on the following:
    Generate the total analysis report in the form of Readme.md file with descriptive answers. 
    Do not blatantly copy the plan and results. Mix them together to form a good research report.
    It should also contain the plots stored by the code in the same project folder.
    - Guidelines: {plan}
    - Code: {code}
    - Results: {dictionary}

    **Write only the Readme.md file.**
    """
    
    return send_request(prompt)

# ------------------------------ Main Execution ------------------------------

def execute_code_with_error_handling(df):
    """
    Execute the analysis plan, run the generated code, and handle errors.

    Args:
    - df (pd.DataFrame): The DataFrame to run the analysis on.

    Returns:
    - str: The final README report.
    """
    plan = str(generate_plan(df.head(25)))
    code = str(generate_code(plan))

    with open('log.txt', 'w') as file:
        file.write(plan)
        file.write(code)

    code = code.replace('python', '').strip()
    code = code.replace('```', '').strip()

    error = None
    while True:
        try:
            output = run_code(code, df)
            print(f"Code executed successfully. Output:\n{output}")
            dictionary = str(output)
            report = str(generate_report(plan, code, dictionary))
            with open('log.txt', 'a') as file:
                file.write(dictionary)
                file.write(report)
            return report

        except Exception as e:
            # Log error with traceback
            error_message = str(e)
            traceback_message = traceback.format_exc()
            print(f"Error detected: {error_message}")
            print(f"Stack trace:\n{traceback_message}")
            with open('log.txt', 'a') as file:
                file.write(f"Error: {error_message}\n")
                file.write(f"Stack trace:\n{traceback_message}\n\n")
            
            # Fix the code and retry
            code = fix_code(code, error_message)
            code = code.replace('python', '').strip()
            code = code.replace('```', '').strip()

            if error == error_message:
                print("Repeated error detected. Stopping execution.")
                return {"error": "Repeated error detected, execution stopped."}

            error = error_message

def main():
    """
    Main function to load the data, generate the report, and save it as a README.md file.
    """
    args = parse_args()
    df = load_data(args.filename)

    # Generate and save the report
    with open('README.md', 'w') as file:
        file.write(execute_code_with_error_handling(df))

if __name__ == "__main__":
    main()
