import numpy as np
import pandas as pd
from pickle import load
from scipy.sparse import  load_npz
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

# Load Data
# articles = pd.read_csv('./data/articles.csv')
articles = pd.read_csv('./module/data/articles.csv')

# KNN recommd function
def recom_knn(art_ID):

    query_artcile = art_ID
    file = "./module/data/newKnn.pickle"
    # file = "./data/newKnn.pickle"
    K = load(open(file,"rb"))
    sparse_matrix = load_npz('./module/data/sparse_matrix.npz')

    ALL_ITEMS = articles['article_id'].unique().tolist()
    leItem = LabelEncoder().fit(ALL_ITEMS)

    index = leItem.transform([query_artcile])
    distances, indices = K.kneighbors(sparse_matrix[index,:].toarray().reshape(1,-1), n_neighbors = 13)
    
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

# rk = recom_knn(541518023)

# for i in rk:
#     print(i.item())


