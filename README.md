# IFRS-17-Calculation-Engine

This project serves as a place to keep the Python code updated and as backups until it can be loaded onto the main IFRS 17 APP.

project is designed to automate and optimize the financial modeling process for insurance companies, with a focus on compliance with IFRS 17 standards. This project integrates sophisticated Python-based financial models with advanced SQL data management techniques, ensuring accurate, efficient, and scalable financial reporting.

Overview of the Project Components
The InsureModel project is divided into several key components, each handling a critical aspect of the financial modeling and reporting process. These components work together to ensure that the entire workflow, from data ingestion to report generation, is seamless and efficient.

1. Data Processing and Modeling (data_processing_and_modeling.py)
This script is the heart of the InsureModel project. It handles all the preliminary steps required to prepare your data for analysis, as well as the application of complex financial models.

Key Functions:
Data Upload and Preprocessing:

The script begins by uploading raw data from CSV files (or other sources) into a Pandas DataFrame.
It performs essential preprocessing tasks such as handling missing values, converting data types, and normalizing data. These steps ensure that the data is clean and in the correct format for further analysis.
GMM and PAA Model Application:

The Generalized Method of Moments (GMM) and Premium Allocation Approach (PAA) models are at the core of this script. These models are applied to the preprocessed data to estimate financial metrics such as liabilities, premiums, and cash flows.
GMM is particularly useful for dealing with complex financial data, allowing for the estimation of parameters when the traditional assumptions of other methods may not hold.
PAA is used for simplified measurement of short-duration contracts, providing a streamlined approach to calculating insurance liabilities and recognizing revenue.
Report Generation:

After applying the models, the script generates comprehensive financial reports, including visualizations and CSV files. These reports provide detailed insights into the financial status of insurance contracts, making them ready for submission or further analysis.
2. SQL Operations (sql_operations.py)
This script manages the backend data operations, leveraging SQL for advanced data manipulation, storage, and retrieval tasks. It is designed to ensure that data is efficiently processed and stored, ready for analysis and reporting.

Key Functions:
Data Upload to MySQL:

This function uploads the preprocessed data to a MySQL database. It ensures that large datasets are stored efficiently, facilitating advanced SQL queries and operations.
Executing Stored Procedures:

The script includes functionality to call stored procedures within the MySQL database. Stored procedures allow for the execution of complex, reusable SQL operations, making data management more efficient and standardized.
Creating SQL Views:

SQL views are created to simplify data retrieval and analysis. The script includes a function that joins multiple tables to create a view, providing a unified perspective on related datasets. For instance, a view might join tables containing expected and actual cash flows, facilitating easy comparison and analysis.
CTE and Window Functions:

The script demonstrates the use of Common Table Expressions (CTEs) and window functions to perform complex queries. These advanced SQL techniques are used to calculate cumulative metrics, perform rolling calculations, and more. For example, the script might calculate cumulative premiums over time for each contract using a window function.
3. GMM Engine (GMM_Engine.py)
This module implements the Generalized Method of Moments (GMM) model, a powerful statistical tool used for estimating the parameters of econometric models. GMM is particularly suited for financial data where traditional assumptions (such as normal distribution) may not hold.

Key Functions:
Parameter Estimation: GMM estimates the parameters of models using moment conditions derived from the data, allowing for robust and flexible modeling.
Application to Insurance Contracts: In the context of IFRS 17, GMM is used to estimate liabilities and other key financial metrics, ensuring that financial statements accurately reflect the underlying risks and obligations.
4. PAA Engine (PAA_Engine.py)
The PAA Engine is designed for the simplified measurement of short-duration insurance contracts, which is a requirement under IFRS 17.

Key Functions:
Revenue Recognition: The PAA engine calculates insurance liabilities and recognizes revenue over the coverage period.
Simplified Model: PAA provides a streamlined approach compared to more complex models like GMM, making it ideal for contracts with a shorter duration.
5. Data Visualization and Reporting
Both the data_processing_and_modeling.py and sql_operations.py scripts include features for data visualization and reporting. This ensures that stakeholders can easily interpret the results of the financial models.

Key Functions:
Line Plots and Trend Analysis: The results from the GMM and PAA models are visualized using line plots, allowing for the analysis of trends over time, such as the evolution of liabilities or cumulative premiums.
CSV Export: All key results are exported to CSV files, ensuring that they can be easily shared, reviewed, or integrated into other systems.
6. Integration and Deployment
The project is designed with integration and scalability in mind. By separating the data processing, modeling, and SQL operations into distinct scripts, the system can be easily integrated into existing workflows or scaled to handle larger datasets or more complex analyses.

Key Functions:
Modular Design: The clear separation of concerns makes it easy to extend or modify the system. For example, additional financial models can be added to the data_processing_and_modeling.py script without affecting the SQL operations.
Deployment Readiness: The project is set up to be easily deployable within a larger financial system, whether on local servers or cloud environments. With its clear structure and extensive use of SQL, it can be integrated with existing databases and reporting tools.
