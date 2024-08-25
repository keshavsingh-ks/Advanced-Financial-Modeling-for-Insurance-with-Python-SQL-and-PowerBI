import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from GMM_Engine import GMMEngine  # Assuming GMMEngine is defined in GMM_Engine.py
from PAA_Engine import PAAEngine  # Assuming PAAEngine is defined in PAA_Engine.py

# 1. Data Upload and Preprocessing
def upload_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df.fillna(0, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# 2. Apply GMM & PAA Models
def apply_models(all_data):
    gmm = GMMEngine()
    paa = PAAEngine()
    gmm_results = gmm.apply(all_data)
    paa_results = paa.apply(all_data)
    return gmm_results, paa_results

# 3. Visualize Results
def generate_reports(gmm_results, paa_results):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=gmm_results, x='Date', y='Liability')
    plt.title('Liability Over Time (GMM)')
    plt.show()
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=paa_results, x='Date', y='Premiums')
    plt.title('Premiums Over Time (PAA)')
    plt.show()
    
    gmm_results.to_csv('GMM_Results.csv', index=False)
    paa_results.to_csv('PAA_Results.csv', index=False)

# Main Execution
if __name__ == "__main__":
    file_path = 'insurance_data.csv'  # Path to your data file
    df = upload_and_preprocess_data(file_path)
    gmm_results, paa_results = apply_models(df)
    generate_reports(gmm_results, paa_results)