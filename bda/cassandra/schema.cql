CREATE KEYSPACE IF NOT EXISTS retail
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
USE retail;

-- Query 1: look up one customer's segment
CREATE TABLE IF NOT EXISTS customer_segments (
  customer_id int PRIMARY KEY, recency int, frequency int, monetary double, cluster int, segment text);

-- Query 2: list customers in a segment, biggest spenders first
CREATE TABLE IF NOT EXISTS customers_by_segment (
  segment text, monetary double, customer_id int, recency int, frequency int,
  PRIMARY KEY ((segment), monetary, customer_id)) WITH CLUSTERING ORDER BY (monetary DESC, customer_id ASC);

-- Query 3: segment dashboard numbers
CREATE TABLE IF NOT EXISTS segment_summary (
  segment text PRIMARY KEY, customers int, avg_recency double, avg_frequency double, avg_monetary double, total_revenue double);
