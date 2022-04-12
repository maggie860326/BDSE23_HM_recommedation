#!/usr/bin/python3

from pyspark.sql import SparkSession

# get spark session
spark = SparkSession\
        .builder\
        .getOrCreate()

# import packages
import sys
import pandas as pd
import pyspark.pandas as ps
import numpy as np
from timeit import timeit
import gc
import pyspark.sql.functions as sf
from pyspark.context import SparkContext
from pyspark.sql.functions import array_max
from pyspark.ml.feature import StringIndexer, IndexToString
from pyspark.pandas.config import set_option, reset_option
from dateutil.relativedelta import relativedelta
from pyspark.sql.types import (
    DateType, DoubleType, FloatType, IntegerType, StringType, StructField, StructType
)

# import self-defined module
import module.time_split_cv as time_split_cv

# set conf
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)
ps.set_option("compute.default_index_type", "distributed")
set_option("compute.ops_on_diff_frames", True)

# get argument
TRAIN_PERIOD = int(sys.argv[1])
print(f"\n\n \
	==================================================\n \
	========= TRAIN_PERIOD = {TRAIN_PERIOD} =========\n \
	==================================================\n\n")

# def main():
print(f"\n\n \
    ==================================================\n \
    ================== 1. Load data ==================\n \
    ==================================================\n\n")
tran_ps = ps.read_parquet('/user/HM_parquet/transactions_train.parquet').drop(['price', 'sales_channel_id'], axis=1)

tran_ps.set_index('t_dat',inplace=True)
tran_ps['start_test'] = ''
tran_ps['split_id'] = ''

print(f"\n\n \
    ==================================================\n \
    ======= 2. Split and concat data by time =========\n \
    ==================================================\n\n")
split_data, split_id = time_split_cv.split(tran_ps,train_period=TRAIN_PERIOD,test_period=7,stride=30,show_progress=True)
split_data.reset_index(inplace=True)
del tran_ps


print(f"\n\n \
    ==================================================\n \
    ===== 3.Parameter grid table cross split_id ======\n \
    ==================================================\n\n")
para_cross_split = time_split_cv.make_para_cross_split_table(split_id)

print(f"\n\n \
    ==================================================\n \
    ===== 4. Join split_data parameter grid table ====\n \
    ==================================================\n\n")

join_data = split_data.join(para_cross_split.set_index('split_id'), on='split_id')
# join_data.set_index('t_dat',inplace=True)
join_data['train_period'] = TRAIN_PERIOD

del split_data, para_cross_split
df = join_data.to_spark()
del join_data

gc.collect()

print(f"\n\n \
    ==================================================\n \
    ===== 5. Train SVD model by pandas_UDF ===========\n \
    ==================================================\n\n")
schema = StructType(
    [
        StructField("train_period", IntegerType(), True),
        StructField('start_test', DateType(),True),
        StructField("n_factors", IntegerType(), True),
        StructField("n_epochs", IntegerType(), True),
        StructField('reg_all', FloatType(),True),
        StructField('rmse', FloatType(),True),
        StructField('map12', FloatType(),True),
     ]
)

results = df.groupby('group_id').applyInPandas(time_split_cv.time_split_hyperparameter_search, schema)
del df
gc.collect()

# results.show(5)

print(f"\n\n \
    ==================================================\n \
    ===== 6. Save result table to parquet ============\n \
    ==================================================\n\n")
results.write.parquet(f'/user/HM_parquet/SVD_model/params/para{TRAIN_PERIOD}.parquet',mode='overwrite',partitionBy='rmse')

print(f"\n\n \
    ==================================================\n \
    =====================  存檔完成 ===================\n \
    ==================================================\n\n")

    
## timeit 
# print(f"\n\n \
# ==================================================\n \
# ================== Start Timeit ==================\n \
# ==================================================\n\n")
# t = timeit('main()','gc.enable()', number=1)
# print(f"\n\n \
# ==================================================\n \
# ================== 執行時長: {t} ==================\n \
# ==================================================\n\n")

spark.stop()
