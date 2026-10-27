#!/usr/bin/env bash
# Usage: ./mapreduce/run_mapreduce.sh local|hadoop
set -euo pipefail
MODE=${1:-local}
IN=data/online_retail_clean.csv
OUT=output/mr_rfm.tsv
mkdir -p output
if [ "$MODE" = "local" ]; then
  # Same contract as Hadoop Streaming: map -> sort by key -> reduce
  python3 mapreduce/mapper_rfm.py < "$IN" | sort -k1,1 | python3 mapreduce/reducer_rfm.py > "$OUT"
else
  hdfs dfs -mkdir -p /bda/input && hdfs dfs -put -f "$IN" /bda/input/
  hdfs dfs -rm -r -f /bda/mr_rfm
  hadoop jar "${HADOOP_HOME}"/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files mapreduce/mapper_rfm.py,mapreduce/reducer_rfm.py \
    -mapper "python3 mapper_rfm.py" -reducer "python3 reducer_rfm.py" \
    -input /bda/input/online_retail_clean.csv -output /bda/mr_rfm
  hdfs dfs -cat /bda/mr_rfm/part-* > "$OUT"
fi
echo "MapReduce RFM rows: $(wc -l < "$OUT")  -> $OUT"
