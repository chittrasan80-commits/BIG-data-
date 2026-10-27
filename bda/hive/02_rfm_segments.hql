USE retail;

DROP TABLE IF EXISTS rfm;
CREATE TABLE rfm AS
SELECT customer_id,
       DATEDIFF('2011-12-10', MAX(invoice_date)) AS recency,
       COUNT(DISTINCT invoice_no)                AS frequency,
       ROUND(SUM(amount), 2)                     AS monetary
FROM clean_retail GROUP BY customer_id;

DROP TABLE IF EXISTS rfm_scored;
CREATE TABLE rfm_scored AS
SELECT customer_id, recency, frequency, monetary,
       NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
       NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
       NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score
FROM rfm;

DROP TABLE IF EXISTS customer_segments_hive;
CREATE TABLE customer_segments_hive AS
SELECT *,
  CASE WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
       WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
       WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
       WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
       WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating'
       ELSE 'Needs Attention' END AS segment
FROM rfm_scored;

SELECT segment, COUNT(*) AS customers, ROUND(AVG(monetary),2) AS avg_spend, ROUND(SUM(monetary),2) AS revenue
FROM customer_segments_hive GROUP BY segment ORDER BY revenue DESC;

SELECT country, ROUND(SUM(amount),2) AS revenue FROM clean_retail GROUP BY country ORDER BY revenue DESC LIMIT 10;

SELECT DATE_FORMAT(invoice_date,'yyyy-MM') AS month, ROUND(SUM(amount),2) AS revenue
FROM clean_retail GROUP BY DATE_FORMAT(invoice_date,'yyyy-MM') ORDER BY month;
