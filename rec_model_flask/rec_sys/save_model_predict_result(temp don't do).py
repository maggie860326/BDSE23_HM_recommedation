import operator
import pickle
import numpy as np
import time
from pathlib import Path
from load_cus_art_mapping import load_cus_art_mapping

directory = Path(__file__).resolve().parent
with open(directory/"rec_svd_model.pkl", 'rb') as f:
   rec_algo = pickle.load(f)
   
art_df,cust_df,trans_df = load_cus_art_mapping()
cust_list = cust_df['customer_id'].tolist()
print(cust_list[0:3])
iid2_list = art_df['article_id'].tolist()

art_est_dict = {}

for j in cust_list[0:3]:
	for i in iid2_list[0:30]:
		est = rec_algo.predict(uid = str(j), iid = str(i)).est
		art_est_dict.setdefault(j, {})[i] = est


print(len(art_est_dict))	
#print(art_est_dict.keys())
#print(art_est_dict)
print(art_est_dict.items())

top12_dict_new = {}
for i in art_est_dict.items():
	dict2 = i[1]
	top12_dict=dict(sorted(dict2.items(), key=operator.itemgetter(1), reverse=True)[:12])
	print(i[0])
	print(type(top12_dict))
	print(top12_dict)
	print('-------------')

print(top12_dict_new)

# save data into mysql 
#import mysql.connector
    
#mydb = mysql.connector.connect(
#  host="172.22.33.44",
#  user="root",
#  password="root",
#  database="HM")

#mycursor = mydb.cursor()

#for i in art_est_dict.items():
#    term = i[0]
#    for url in i[1]:
		#sql = """INSERT INTO HM.customer_rec(customer_id, rec_list) VALUES (%s, %s)"""
		#mycursor.execute(sql, (term, url))
		#print(term)
		#print(url)
	
#top12_dict=dict(sorted(art_est_dict.items(), key=operator.itemgetter(1), reverse=True)[:12])

#for key, value in top12_dict.items():
#    print(key, value)

## save dict to json file
import json 
with open("my.json","w") as f:
    json.dump(art_est_dict,f)




 