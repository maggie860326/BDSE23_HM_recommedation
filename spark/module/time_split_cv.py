import pyspark.pandas as ps
from dateutil.relativedelta import relativedelta
import pandas as pd
from module.surpriseSVD import surpriseSVD
from itertools import product
import numpy as np



def split(data,train_period=30, test_period=7, stride=30,show_progress=False):
    
    split_data = ps.DataFrame(columns = ['t_dat','customer_id', 'article_id', 'split_id', 'start_test']).set_index('t_dat',inplace=True)

    end_test = data.index.max()
    start_test = end_test - relativedelta(days=test_period)
    start_train = start_test - relativedelta(days=train_period)
    split_id=0

    while start_train >= data.index.min():

        df = data.loc[start_train:end_test]
        df['start_test']=start_test
        df['split_id'] = split_id
        split_data = ps.concat([split_data,df])

        if(show_progress):
            print("Split_id:",split_id,", Train period:",start_train,"-" , start_test, ", test period", start_test, "-", end_test)

        # update dates:
        end_test = end_test - relativedelta(days=stride)
        start_test = end_test - relativedelta(days=test_period)
        start_train = start_test - relativedelta(days=train_period)
        split_id += 1
    
    return split_data, split_id

def make_para_cross_split_table(split_id):
    paras = list(
        product(
            [25,50,100,150,200],
            [20,30,40,50],
            [0.01]
        )
    )
    paras_grid = ps.DataFrame(paras,columns= ['n_factors','n_epochs','reg_all'])
    
    # 製作 split_id 表
    split_id_ps = ps.DataFrame({'split_id': range(split_id)})
    
    # 將 paras_grid 與 split_id 做 cross join
    paras_grid['key'] = 1
    split_id_ps['key'] = 1
    para_cross_split = ps.merge(paras_grid, split_id_ps, on ='key').drop('key')
    
    del split_id_ps
    
    # 將 cross join 後的表新增遞增的 group_id 欄位，之後要用來做 pandas_udf 的 groupby
    para_cross_split['group_id'] = 0
    para_cross_split['group_id'] = np.arange(len(para_cross_split)).tolist()

    return para_cross_split

    
def time_split_hyperparameter_search(data):

    paras = {
        'n_factors':data.n_factors.values[0], 
        'n_epochs':data.n_epochs.values[0], 
        'reg_all':data.reg_all.values[0]
    }
    
    test_index = data['t_dat'] > data['start_test'][0]
    train_data = data.loc[~test_index]
    test_data = data.loc[test_index]
    
    model = surpriseSVD()
    rmse, map12 = model.train_SVD(train_data, test_data, paras)
    
    paras.update({
        'stride': data.stride.values[0],
        'start_test' : data.start_test.values[0],
        'rmse' : rmse,
        'map12' : map12
    })
    
    results = pd.DataFrame([paras])
    
    return results