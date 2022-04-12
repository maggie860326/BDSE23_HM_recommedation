#!/bin/bash
export PYARROW_IGNORE_TIMEZONE='1'

spark-submit\
  --name BDSE23_team4\
  --master yarn \
  --driver-memory 4G \
  --driver-cores 1 \
  --executor-memory 6G \
  --executor-cores 1 \
  --num-executors 99 \
  --deploy-mode client\
  --conf spark.executorEnv.SURPRISE_DATA_FOLDER="/home/hadoop"\
  --conf spark.executorEnv.PYARROW_IGNORE_TIMEZONE='1'\
  --py-files module.zip\
  __main__.py $1




#  --conf spark.kryoserializer.buffer.max=512m\
#  --conf spark.default.parallelism=100\
#  --conf spark.sql.shuffle.partitions=1000\
