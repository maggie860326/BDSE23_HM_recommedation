import pickle
import numpy as np
import time
from pathlib import Path
import operator
from load_cus_art_mapping import load_cus_art_mapping

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
	
directory = Path(__file__).resolve().parent

def rec_model():
  with open(directory/"rec_svd_model.pkl", 'rb') as f:
     rec_algo = pickle.load(f)
     est = rec_algo.predict(uid = '00000dbacae5abe5e23885899a1fa44253a17956c6d1c3d25f88aa139fdfc657', iid = '568601043').est
  return est


def rec_model_several(user):
  with open(directory/"rec_svd_model.pkl", 'rb') as f:
   rec_algo = pickle.load(f)
  art_df,cust_df,trans_df = load_cus_art_mapping()
  #uid2 = str(cust_df['customer_id'][2])
  iid2_list = art_df['article_id'].tolist()
  
  est_list = []
  for i in iid2_list: 
    est2 = rec_algo.predict(uid = user, iid = str(i)).est
    est_list.append(est2)
  
  rec_list = sorted(est_list)[0:13]
  return est_list,rec_list,iid2_list[0:13]

def rec_model_several_dict(user):
  
  with open(directory/"rec_svd_model.pkl", 'rb') as f:
   rec_algo = pickle.load(f)
  
  art_df,cust_df,trans_df = load_cus_art_mapping()
  
  iid2_list = art_df['article_id'].tolist()
  
  rec_model_dict = {}
  for i in iid2_list:
     est = rec_algo.predict(uid = user, iid = str(i)).est
     rec_model_dict.setdefault(i,[]).append(est)
  
  rec_model_dict_top12 = sorted(rec_model_dict.items(), key=operator.itemgetter(1))[:12]
  return rec_model_dict_top12

