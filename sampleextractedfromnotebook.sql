-- Create a table from a CSV file (Python code is used to generate the query)
CREATE TABLE IF NOT EXISTS `table_name` (
    `column1` TEXT,
    `column2` TEXT,
    -- Add more columns as needed
);

-- Insert data into the table (Python code generates the insert statement)
INSERT INTO `table_name` (`column1`, `column2`) VALUES ('value1', 'value2');

-- Create a view by joining two tables
CREATE OR REPLACE VIEW Expected_Actual_Cashflow_View AS
SELECT 
    ec.`Premiums`,
    ac.`Claims`
FROM 
    Expected_Cashflow_Statement ec
JOIN 
    Actual_Cashflow_Statement ac ON ec.`Renewal Commission` = ac.`Renewal Commission`;

-- Query using CTE and window function to calculate cumulative premiums
WITH CTE_CumulativePremiums AS (
    SELECT
        `Premiums`,
        SUM(`Premiums`) OVER (ORDER BY `Renewal Commission`) AS CumulativePremiums
    FROM Expected_Cashflow_Statement
)
SELECT * FROM CTE_CumulativePremiums;
