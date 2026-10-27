"""Load PySpark output into Cassandra and run demo queries.  pip install cassandra-driver pandas"""
import os, pandas as pd
from cassandra.cluster import Cluster
from cassandra.concurrent import execute_concurrent_with_args

s = Cluster([os.environ.get("CASSANDRA_HOST", "127.0.0.1")]).connect()
for stmt in open("cassandra/schema.cql").read().split(";"):
    stmt = "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("--")).strip()
    if stmt: s.execute(stmt)
s.set_keyspace("retail")

seg = pd.read_csv("output/pyspark_segments.csv")
summ = pd.read_csv("output/segment_summary.csv")
q1 = s.prepare("INSERT INTO customer_segments (customer_id,recency,frequency,monetary,cluster,segment) VALUES (?,?,?,?,?,?)")
q2 = s.prepare("INSERT INTO customers_by_segment (segment,monetary,customer_id,recency,frequency) VALUES (?,?,?,?,?)")
q3 = s.prepare("INSERT INTO segment_summary (segment,customers,avg_recency,avg_frequency,avg_monetary,total_revenue) VALUES (?,?,?,?,?,?)")
rows = lambda df, cols: [tuple(v.item() if hasattr(v, "item") else v for v in r) for r in df[cols].itertuples(index=False)]
for st, df, cols in [(q1, seg, ["customer_id","recency","frequency","monetary","cluster","segment"]),
                     (q2, seg, ["segment","monetary","customer_id","recency","frequency"]),
                     (q3, summ, ["segment","customers","avg_recency","avg_frequency","avg_monetary","total_revenue"])]:
    for ok, err in execute_concurrent_with_args(s, st, rows(df, cols)):
        if not ok: raise err

print("Customers loaded:", s.execute("SELECT COUNT(*) FROM customer_segments").one()[0])
cid = int(seg.customer_id.iloc[0])
print("Lookup:", s.execute("SELECT * FROM customer_segments WHERE customer_id=%s", (cid,)).one())
top = seg.segment.iloc[0]
print(f"Top 5 spenders in '{top}':")
for r in s.execute("SELECT customer_id, monetary FROM customers_by_segment WHERE segment=%s LIMIT 5", (top,)): print("  ", r)
print("Segment summary:")
for r in s.execute("SELECT * FROM segment_summary"): print("  ", r)
