import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from pyspark.sql.types import StringType,DoubleType,IntegerType,StructType,StructField,FloatType
from pyspark.sql.functions import pandas_udf,struct,PandasUDFType
from pyspark.sql import SparkSession
from sklearn.metrics import accuracy_score,precision_score,recall_score,roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

spark = SparkSession.builder \
               .appName('sklearn_using_spark') \
               .getOrCreate()

## iris dataset
data = load_iris(as_frame=True)
iris = pd.concat([data['data'],data['target']],axis=1)
iris['id'] = 1
iris['y'] = iris['target']
iris2 = iris.drop(columns=['target'])
final_df=iris2
X_columns = final_df.drop(columns=['id','y']).columns
y_columns = 'y'

final_df_spark = spark.createDataFrame(final_df)

def model_results_per_id(key,df):
   key = int(df.id.unique()[0])
   X=df[X_columns]
   y=df[y_columns]
   X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=42)
   dtree_model = DecisionTreeClassifier(max_depth = 2).fit(X_train, y_train)
   y_pred = dtree_model.predict(X_test)
   accuracy=accuracy_score(y_test,y_pred).tolist()
   model_results = pd.DataFrame([[key,accuracy]],columns=['id','accuracy'])
   return model_results

model_results_by_id2 = final_df_spark.groupBy('id').applyInPandas(model_results_per_id,schema="id long,accuracy double").show()
final_df_spark.groupBy('id').applyInPandas(model_results_per_id,schema="id long,accuracy double").explain()
final_df_spark.groupBy('id').applyInPandas(model_results_per_id,schema="id long,accuracy double").explain(extended = True)
