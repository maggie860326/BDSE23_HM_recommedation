import pickle
import numpy as np
import time
from pathlib import Path
import operator
from module.load_cus_art_mapping import load_cus_art_mapping
from surprise import *
	
directory = Path(__file__).resolve().parent

def rec_model_several(user):
  with open(directory/"rec_svd_model.pkl", 'rb') as f:
    rec_algo = pickle.load(f)
  art_df,cust_df,trans_df,bi_df = load_cus_art_mapping()
  #uid2 = str(cust_df['customer_id'][2])
  iid2_list = art_df['article_id'].tolist()
  
  est_list = []
  for i in iid2_list: 
    est2 = rec_algo.predict(uid = user, iid = str(i)).est
    est_list.append(est2)
  
  rec_list = sorted(est_list)[0:12]
  return est_list,rec_list,iid2_list[0:12]

def rec_model_several_dict(user):
  
  with open(directory/"rec_svd_model.pkl", 'rb') as f:
   rec_algo = pickle.load(f)
  
  art_df,cust_df,trans_df,bi_df = load_cus_art_mapping()
  
  iid2_list = art_df['article_id'].tolist()
  
  rec_model_dict = {}
  for i in iid2_list:
     est = rec_algo.predict(uid = user, iid = str(i)).est
     rec_model_dict.setdefault(i,[]).append(est)
  
  rec_model_dict_top12 = sorted(rec_model_dict.items(), key=operator.itemgetter(1))[:12]
  return rec_model_dict_top12

