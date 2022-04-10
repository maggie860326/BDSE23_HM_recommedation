#!/bin/bash

spark-submit\
  --name BDSE23_team4\
  --master yarn \
  --driver-memory 6G \
  --driver-cores 1 \
  --executor-memory 6G \
  --executor-cores 2 \
  --num-executors 99 \
  --deploy-mode client\
  --conf spark.kryoserializer.buffer.max=512m\
  --conf spark.executorEnv.SURPRISE_DATA_FOLDER="/home/hadoop"\
  --py-files module.zip\
  main.py $1

