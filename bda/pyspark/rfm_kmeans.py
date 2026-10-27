"""PySpark: RFM features -> log + standardise -> KMeans (k by silhouette) -> named segments."""
import sys, os
from pyspark.sql import SparkSession, Window, functions as F
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

SRC = sys.argv[1] if len(sys.argv) > 1 else "data/online_retail_clean.csv"
REF = "2011-12-10"
os.makedirs("output", exist_ok=True)

spark = SparkSession.builder.appName("CustomerSegmentation").master("local[*]") \
    .config("spark.sql.shuffle.partitions", "8").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df = (spark.read.csv(SRC, header=True, inferSchema=True)
      .filter(~F.col("InvoiceNo").cast("string").startswith("C"))
      .filter((F.col("Quantity") > 0) & (F.col("UnitPrice") > 0) & F.col("CustomerID").isNotNull())
      .withColumn("amount", F.col("Quantity") * F.col("UnitPrice"))
      .withColumn("d", F.to_date("InvoiceDate")))

rfm = (df.groupBy(F.col("CustomerID").cast("int").alias("customer_id"))
       .agg(F.datediff(F.lit(REF).cast("date"), F.max("d")).alias("recency"),
            F.countDistinct("InvoiceNo").alias("frequency"),
            F.round(F.sum("amount"), 2).alias("monetary")))

feat = rfm.select("*", *[F.log1p(c).alias(f"l_{c}") for c in ("recency", "frequency", "monetary")])
vec = VectorAssembler(inputCols=["l_recency", "l_frequency", "l_monetary"], outputCol="raw").transform(feat)
scaled = StandardScaler(inputCol="raw", outputCol="features", withMean=True, withStd=True).fit(vec).transform(vec)

best_k, best_s, best_model = None, -1.0, None
for k in range(3, 7):  # k>=3 so segments are business-useful
    m = KMeans(k=k, seed=42, featuresCol="features").fit(scaled)
    s = ClusteringEvaluator().evaluate(m.transform(scaled))
    print(f"k={k} silhouette={s:.4f}")
    if s > best_s: best_k, best_s, best_model = k, s, m
print(f"Chosen k={best_k} (silhouette {best_s:.4f})")

pred = best_model.transform(scaled).withColumnRenamed("prediction", "cluster")
prof = pred.groupBy("cluster").agg(F.avg("recency").alias("r"), F.avg("frequency").alias("f"),
                                   F.avg("monetary").alias("m")).toPandas()
# Rank clusters: high frequency & monetary, low recency = best
for c in ("r", "f", "m"):
    prof[c + "n"] = prof[c] / prof[c].max()
prof["score"] = prof["fn"] + prof["mn"] - prof["rn"]
order = prof.sort_values("score", ascending=False)["cluster"].tolist()
NAMES = {2: ["Champions", "Hibernating"],
         3: ["Champions", "At Risk", "Hibernating"],
         4: ["Champions", "Loyal Customers", "At Risk", "Hibernating"],
         5: ["Champions", "Loyal Customers", "Potential Loyalists", "At Risk", "Hibernating"],
         6: ["Champions", "Loyal Customers", "Potential Loyalists", "At Risk", "Hibernating", "Lost"]}
label = {c: NAMES[best_k][i] for i, c in enumerate(order)}
mapping = spark.createDataFrame([(int(c), n) for c, n in label.items()], ["cluster", "segment"])
result = pred.join(mapping, "cluster").select("customer_id", "recency", "frequency", "monetary", "cluster", "segment")

result.toPandas().to_csv("output/pyspark_segments.csv", index=False)
summary = result.groupBy("segment").agg(F.count("*").alias("customers"),
          F.round(F.avg("recency"), 1).alias("avg_recency"), F.round(F.avg("frequency"), 1).alias("avg_frequency"),
          F.round(F.avg("monetary"), 2).alias("avg_monetary"), F.round(F.sum("monetary"), 2).alias("total_revenue")
          ).orderBy(F.desc("total_revenue"))
summary.show(truncate=False)
summary.toPandas().to_csv("output/segment_summary.csv", index=False)
spark.stop()
