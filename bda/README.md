# E-Commerce Customer Segmentation using Big Data (CCS334)
Dataset: UCI Online Retail · SDG 8 · Team 5 (Chittrasan, Harish S)

RFM (Recency, Frequency, Monetary) customer segmentation across the Big Data stack:

| Stage | Tool | Files |
|---|---|---|
| Batch RFM | Hadoop MapReduce (Streaming, Python) | `mapreduce/` |
| SQL analytics + NTILE RFM scoring | Apache Hive | `hive/` |
| Clustering (KMeans, silhouette-chosen k) | PySpark MLlib | `pyspark/rfm_kmeans.py` |
| NoSQL serving layer | Apache Cassandra | `cassandra/` |

Input: `data/online_retail_clean.csv` with columns
`InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country`.

## Run
```bash
pip install -r requirements.txt
bash mapreduce/run_mapreduce.sh local     # or: hadoop   (on a cluster)
python pyspark/rfm_kmeans.py              # -> output/pyspark_segments.csv, segment_summary.csv
CASSANDRA_HOST=127.0.0.1 python cassandra/load_cassandra.py
# Hive: beeline -u jdbc:hive2://localhost:10000 --hivevar data_dir=hdfs:///bda/input -f hive/01_create_tables.hql -f hive/02_rfm_segments.hql
```
The GitHub Actions workflow (`.github/workflows/pipeline.yml`) runs all four stages on every push.
Snapshot date for recency is 2011-12-10 (day after the last invoice).
