
import pandas as pd
from dateutil.relativedelta import *
from TimeBasedCV import TimeBasedCV
from surpriseSVD import surpriseSVD as svd
import sys
from timeit import timeit

tscv = TimeBasedCV(freq='days')
model = svd()

def main():
    transactions = pd.read_parquet('../data/HM_parquet/transactions_train.parquet')
        
    train_period = sys.argv[1]
    
    # 做 time based split
    test_period, stride = 7, 30
    index_output = tscv.split(transactions, date_column='t_dat', train_period=train_period, test_period=test_period, stride=stride,show_progress=True)

    # 做 time based CV
    scores = pd.DataFrame(columns=["train_period","val_period","stride"])

    for train_index, val_index in index_output:
        train_data = transactions.loc[train_index]
        val_data = transactions.loc[val_index]
        # 取得val開始日期
        val_data.reset_index(inplace=True, drop=True)
        start_val = val_data['t_dat'][0]
        # 呼叫訓練模型的function
        one_fold_scores = model.train_SVD(train_data, val_data, train_period, test_period, stride, start_val)
        scores = pd.concat([scores,one_fold_scores], axis=0 ,ignore_index=True)

    scores.to_parquet(f'../model/params/params_SVD_stride30/surprise_SVD_train{train_period}.parquet')
    print(f"完成存檔: surprise_SVD_train{train_period}.parquet")
    
    

if __name__ == "__main__":
    t = timeit('main()', 'from __main__ import main', number=1)
    print(f"執行時長: {t}")