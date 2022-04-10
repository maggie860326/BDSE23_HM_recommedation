import pandas as pd
# from surprise import NormalPredictor
from surprise import Dataset
from surprise import Reader
from surprise import SVDpp,SVD
from surprise import accuracy
from surprise.model_selection import train_test_split
from collections import defaultdict
import numpy as np
import module.average_precision as metrics

class surpriseSVD():
    def __init__(self):
        self = self

    def get_top_n(self, predictions, n=12):
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

    def get_set(self,df):
        reader = Reader(rating_scale=(1, 500))
        data_set = Dataset.load_from_df(df[['customer_id','article_id','rating']], reader)
        return data_set

    def get_rating_set(self,df):
        rating = df[['customer_id','article_id','split_id']].groupby(['customer_id','article_id']).count().reset_index()
        rating.columns = ['customer_id','article_id','rating']
        rating_set = self.get_set(rating)
        return rating_set


    def train_SVD(self, train_data, test_data, paras={}):
        
        ## 讀取評分資料為surprise可以訓練的格式
        trainset = self.get_rating_set(train_data)
        testset = self.get_rating_set(test_data)

        ## rmse 需要的資料
        testset2 = [testset.df.loc[i].to_list() for i in range(len(testset.df))]

        ## map@k testing 需要產的資料
        test_data.loc[:,'rating']=0
        test_processed = self.get_set(test_data)
        NA, test2 = train_test_split(test_processed, test_size=1.0)

        # ======= 消費者的實際購買清單 =======
        test_data['article_id'] = test_data['article_id'].astype('str')
        test_uni = test_data.drop_duplicates(subset=['customer_id', 'article_id'], keep='first')
        buy_n = test_uni[['customer_id','article_id']].groupby('customer_id')['article_id'].apply(list).to_dict()

        cust_actual_list = []
        for uid, user_ratings in buy_n.items():
            cust_pred_tuple = (uid, [iid for iid in user_ratings])
            cust_actual_list.append(cust_pred_tuple)

        # ======= 訓練 SVD 模型 =======
        algo = SVD(random_state=42,**paras)

        # 訓練模型
        algo.fit(trainset.build_full_trainset())

        ##### rmse #####
        predictions = algo.test(testset2)
        rmse = accuracy.rmse(predictions)

        ##### map@k #####
        predictions_map = algo.test(test2)
        # est = [i.est for i in predictions_map] 

        ##  消費者的預測清單 
        top_n = self.get_top_n(predictions=predictions_map, n=12)

        cust_pred_list = []
        for uid, user_ratings in top_n.items():
            cust_pred_tuple = (uid, [str(iid) for (iid, _) in user_ratings])
            cust_pred_list.append(cust_pred_tuple)

        final_list = list(zip(cust_actual_list, cust_pred_list))

        # map@k計算 
        mapk_list = []
        for i in range(len(final_list)):
            map_k = metrics.mapk([final_list[i][0][1]],[final_list[i][1][1]],12)
            mapk_list.append(map_k)

        map_k = sum(mapk_list)/len(mapk_list)

        return rmse, map_k