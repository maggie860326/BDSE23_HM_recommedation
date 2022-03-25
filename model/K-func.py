import numpy as np
import pandas as pd
from pickle import load
from scipy.sparse import coo_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

# Load Data
customers = pd.read_csv('../data/customers.csv')
articles = pd.read_csv('../data/articles.csv')
transactions = pd.read_csv('../data/transactions_train.csv')

# KNN recommd function
def recom_knn(art_ID):

    query_artcile = art_ID
    file = "../data/newKnn.pickle"
    K = load(open(file,"rb"))
    
    ALL_USERS = customers['customer_id'].unique().tolist()
    ALL_ITEMS = articles['article_id'].unique().tolist()

    leUser = LabelEncoder().fit(ALL_USERS)
    transactions['user_id'] = leUser.transform(transactions['customer_id'])
    leItem = LabelEncoder().fit(ALL_ITEMS)
    transactions['item_id'] = leItem.transform(transactions['article_id'])

    col = transactions['user_id'].values
    row = transactions['item_id'].values
    one = np.ones(transactions.shape[0])
    coo = coo_matrix((one, (row, col)), shape=(len(ALL_ITEMS), len(ALL_USERS)))
    csr = coo.tocsr()

    model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
    model_knn.fit(csr)
    index = leItem.transform([query_artcile])
    distances, indices = K.kneighbors(csr[index,:].toarray().reshape(1,-1), n_neighbors = 6)
    
    article = []
    distance = []

    for i in range(0, len(distances.flatten())):
        if i != 0:
            article.append(leItem.inverse_transform([indices.flatten()[i]]))
            distance.append(distances.flatten()[i]) 
           

    m=pd.Series(article,name='article')
    d=pd.Series(distance,name='distance')
    recommend = pd.concat([m,d], axis=1)
    recommend = recommend.sort_values('distance',ascending=False)
    recom_list = [recommend["article"].iloc[i] for i in range(0,recommend.shape[0])] 
    
    return recom_list

rk = recom_knn(541518023)

for i in rk:
    print(i.item())


