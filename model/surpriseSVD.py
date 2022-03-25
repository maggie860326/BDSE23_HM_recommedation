
import pandas as pd
from dateutil.relativedelta import *
from TimeBasedCV import TimeBasedCV

transactions = pd.read_parquet('../data/HM_parquet/transactions_train.parquet')
customers = pd.read_parquet('../data/HM_parquet/customers.parquet')
articles = pd.read_parquet('../data/HM_parquet/articles.parquet')

tscv = TimeBasedCV(freq='days')
    
# 測試一個月的資料
train_one_month = pd.read_parquet('../data/HM_parquet/train_one_month.parquet')
val_one_month = pd.read_parquet('../data/HM_parquet/val_one_month.parquet')



    
# SVD    
import pandas as pd
from surprise import NormalPredictor
from surprise import Dataset
from surprise import Reader
from surprise import SVDpp,SVD
from surprise import accuracy
from surprise.model_selection import cross_validate,GridSearchCV,train_test_split
from collections import defaultdict
import numpy as np
import ml_metrics as metrics

def get_top_n(predictions, n=12):
    """Return the top-N recommendation for each user from a set of predictions.
    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.
    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n


def get_rating(df):
    rating = df[['customer_id','article_id','price']].groupby(['customer_id','article_id']).count().reset_index()
    rating.columns = ['customer_id','article_id','rating']
    return rating

def data_preprocess(data):
    data_rating = get_rating(data)
    reader = Reader(rating_scale=(1, 500))
    data_set = Dataset.load_from_df(data_rating[['customer_id','article_id','rating']], reader)
    return data_set
    

## 讀取評分資料為surprise可以訓練的格式
trainset = data_preprocess(train_one_month)
testset = data_preprocess(val_one_month)


## 模型訓練與驗證(svd)
scores = pd.DataFrame()
for factors in [25,50,100,150,200]:
    for iterations in [20,30,40,50]:
        for regularization in [0.01]:

            algo = SVD(n_factors = factors,
                       n_epochs=iterations,
                       reg_all=regularization,
                       random_state=42)

            # 訓練模型
            algo.fit(trainset.build_full_trainset())
            # step3 - testing(train_test_split way)
            
            ##### rmse #####
            testset2 = [testset.df.loc[i].to_list() for i in range(len(testset.df))]
            predictions = algo.test(testset2)
            rmse = accuracy.rmse(predictions)

            ## map@k testing需要產的資料
            val_one_month.loc[:,'rating']=0
            test_processed = Dataset.load_from_df(val_one_month[['customer_id','article_id','rating']], reader) 
            NA, test2 = train_test_split(test_processed, test_size=1.0)

            ##### map@k #####
            predictions_map = algo.test(test2)
            # est = [i.est for i in predictions_map] 

            ## ======= 消費者的預測清單 =======
            top_n = get_top_n(predictions_map, n=12)

            cust_pred_list = []
            for uid, user_ratings in top_n.items():
                cust_pred_tuple = (uid, [str(iid) for (iid, _) in user_ratings])
                cust_pred_list.append(cust_pred_tuple)
            
            # ======= 消費者的實際購買清單 =======
            val_one_month['article_id'] = val_one_month['article_id'].astype('str')
            test_uni = val_one_month.drop_duplicates(subset=['customer_id', 'article_id'], keep='first')
            buy_n = test_uni[['customer_id','article_id']].groupby('customer_id')['article_id'].apply(list).to_dict()

            cust_actual_list = []
            for uid, user_ratings in buy_n.items():
                cust_pred_tuple = (uid, [iid for iid in user_ratings])
                cust_actual_list.append(cust_pred_tuple)

            final_list = list(zip(cust_actual_list, cust_pred_list))
            


            #map@k計算 
            mapk_list = []
            for i in range(len(final_list)):
              map_k = metrics.mapk([final_list[i][0][1]],[final_list[i][1][1]],12)
              mapk_list.append(map_k)

            def Average(lst):
                return sum(lst) / len(lst)

            map_k = Average(mapk_list)

            newRow = {
                        # =====填寫參數名稱===============
                        'factors':factors, 
                        'iterations':iterations, 
                        'regularization':regularization, 
                        # ===============================
                        'rmse':rmse,
                        'map@k':map_k
                        }
            print(newRow)
            newDF = pd.DataFrame([newRow])
            scores = pd.concat([scores, newDF], axis=0 ,ignore_index=True)

scores