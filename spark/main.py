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
import time_split_cv

# set conf
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)
ps.set_option("compute.default_index_type", "distributed")
set_option("compute.ops_on_diff_frames", True)

# get argument
TRAIN_PERIOD = sys.argv[1]
print(f"\n \
	==================================================\n \
	========= TRAIN_PERIOD = {TRAIN_PERIOD} =========\n \
	==================================================\n")


print(f"\n \
	==================================================\n \
	================== 1. Load data ==================\n \
	==================================================\n")
tran_ps = ps.read_parquet('/user/HM_parquet/transactions_train.parquet').drop(['price', 'sales_channel_id'], axis=1)

tran_ps.set_index('t_dat',inplace=True)
tran_ps['start_test'] = ''
tran_ps['split_id'] = ''


print(f"\n \
	==================================================\n \
	======= 2. Split and concat data by time =========\n \
	==================================================\n")
split_data, split_id = time_split_cv.split(tran_ps,train_period=TRAIN_PERIOD,test_period=7,stride=30,show_progress=True)
split_data.reset_index(inplace=True)
del tran_ps


print(f"\n \
	==================================================\n \
	===== 3.Parameter grid table cross split_id ======\n \
	==================================================\n")
# para_cross_split = ps.read_parquet('/user/HM_parquet/SVD_model/para_cross_split.parquet')
para_cross_split = time_split_cv.make_para_cross_split_table(split_id)
# para_cross_split.to_parquet('/user/HM_parquet/SVD_model/para_cross_split.parquet')

print(f"\n \
	==================================================\n \
	===== 4. Join split_data parameter grid table ====\n \
	==================================================\n")
join_data = split_data.join(para_cross_split.set_index('split_id'), on='split_id')
join_data.set_index('t_dat',inplace=True)
join_data['stride'] = TRAIN_PERIOD

del split_data, para_cross_split
df = join_data.to_spark()
del join_data

gc.collect()


print(f"\n \
	==================================================\n \
	===== 5. Train SVD model by pandas_UDF ===========\n \
	==================================================\n")
schema = StructType(
    [
        StructField("stride", IntegerType(), True),
        StructField('start_test', DateType(),True),
        StructField("n_factors", IntegerType(), True),
        StructField("n_epochs", IntegerType(), True),
        StructField('reg_all', FloatType(),True),
        StructField('rmse', FloatType(),True),
        StructField('map12', FloatType(),True),
     ]
)

results = df.groupby('group_id').applyInPandas(time_split_cv.time_split_hyperparameter_search, schema)

print(f"\n \
	==================================================\n \
	===== 6. Save result table to parquet ============\n \
	==================================================\n")
results.write.parquet(f'/user/HM_parquet/SVD_model/params/para{TRAIN_PERIOD}.parquet',mode='overwrite',partitionBy='rmse')

print(f"\n \
	==================================================\n \
	======== 7. Show the best parameters =============\n \
	==================================================\n")
results.groupBy(['n_factors','n_epochs','reg_all']).mean('rmse','map12').sort("avg(rmse)").limit(5).show()