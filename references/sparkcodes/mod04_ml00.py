#!/usr/bin/python3
# coding: utf-8

# # Machine Learning Quick Start
# Spark on YARN example:
# bin/spark-submit \
#    --master yarn \
#    --driver-memory 1G \
#    --driver-cores 1 \
#    --executor-memory 1G \
#    --executor-cores 1 \
#    --num-executors 2 \
#    mod04_ml00.py

import numpy as np
import pandas as pd
import pyspark
import sys

from pyspark.sql import SparkSession
import pyspark.sql.functions as fn

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorAssembler, StringIndexer

# Create spark session
spark = SparkSession.builder.appName("iris").getOrCreate()

# Check spark app name
print(spark.sparkContext.appName)

spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)

# load iris.csv into Spark dataframe
#df = spark.read.csv('file:///vagrant/data/iris.csv', header=True, inferSchema=True)
df = spark.read.csv('data/iris.csv', header=True, inferSchema=True)

#df.show(5)
#df.printSchema()
#df.describe().show()
#df.groupBy('species').count().show(10,False)
#df.columns

# vectorize all numerical columns into a single feature column
feature_cols = df.columns[:-1]
assembler = VectorAssembler(inputCols=feature_cols, outputCol='features')
df = assembler.transform(df)

# convert text labels into indices
data = df.select(['features', 'species'])
label_indexer = StringIndexer(inputCol='species', outputCol='label').fit(data)
data = label_indexer.transform(data)

# only select the features and label column
data = data.select(['features', 'label'])

# Reading for machine learning
#data.show(10)
#data.select(['label']).distinct().show()

# Split Data - Train & Test sets
# use Logistic Regression to train on the training set
train, test = data.randomSplit([0.70, 0.30], seed=42)

# Build Logistic Regression Model
# change regularization rate and you will likely get a different accuracy.
reg = 0.01

lr = LogisticRegression(regParam=reg)
model = lr.fit(train)

# predict on the test set
prediction = model.transform(test)

# print prediction
prediction.show(10)

# Evaluate Model
# evaluate the accuracy of the model using the test set
evaluator = MulticlassClassificationEvaluator(metricName='accuracy')
accuracy = evaluator.evaluate(prediction)

# print accuracy 
print(accuracy)

# stop spark session
spark.stop()
