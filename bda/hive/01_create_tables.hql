CREATE DATABASE IF NOT EXISTS retail;
USE retail;

DROP TABLE IF EXISTS raw_retail;
CREATE EXTERNAL TABLE raw_retail (
  invoice_no STRING, stock_code STRING, description STRING, quantity STRING,
  invoice_date STRING, unit_price STRING, customer_id STRING, country STRING)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"")
STORED AS TEXTFILE
LOCATION '${hivevar:data_dir}'
TBLPROPERTIES ("skip.header.line.count" = "1");

DROP VIEW IF EXISTS clean_retail;
CREATE VIEW clean_retail AS
SELECT invoice_no,
       CAST(CAST(customer_id AS DOUBLE) AS INT) AS customer_id,
       TO_DATE(invoice_date) AS invoice_date,
       CAST(quantity AS INT) * CAST(unit_price AS DOUBLE) AS amount,
       country
FROM raw_retail
WHERE invoice_no NOT LIKE 'C%'
  AND CAST(quantity AS INT) > 0 AND CAST(unit_price AS DOUBLE) > 0
  AND customer_id <> '';
