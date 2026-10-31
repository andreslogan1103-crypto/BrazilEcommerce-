import pandas as pd 
from pandasql import sqldf
df = pd.read_csv("olist_orders_dataset.csv")
query = """
SELECT order_status, COUNT(*) as count
FROM df 
GROUP BY order_status
ORDER BY count DESC
"""