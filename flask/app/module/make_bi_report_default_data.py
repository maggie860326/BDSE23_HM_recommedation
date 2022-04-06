import pandas as pd

bi_data_p = pd.read_parquet('C:/Users/Student/Desktop/上課筆記/期末報告/BDSE23_HM_recommedation/flask/app/module/data/transactions_train.parquet',engine='pyarrow')

bi_data_p['t_dat'] = pd.to_datetime(bi_data_p['t_dat'])
bi_data_p['year'] = bi_data_p['t_dat'].dt.year.astype('str')
bi_data_p['month'] = bi_data_p['t_dat'].dt.month.astype('str')

year_filter = bi_data_p['year'].isin(['2018','2019','2020'])

month_filter = bi_data_p['month'].isin(['1','2','3','4','5','6','7','8','9','10','11','12'])

filter_bi = bi_data_p[year_filter & month_filter]

groupby_df = filter_bi[['year','month','price']].groupby(['year','month'])['price'].sum().to_frame('產品總營收').reset_index()

groupby_df.columns = ['年份','月份','產品總營收']
groupby_df['產品總營收'] = groupby_df['產品總營收'].astype('int')
groupby_df['年份'] = groupby_df['年份'].astype('int')
groupby_df['月份'] = groupby_df['月份'].astype('int')
groupby_df.sort_values(['年份','月份'], ascending=[True,True],inplace=True)
	
groupby_df.to_parquet('C:/Users/Student/Desktop/上課筆記/期末報告/BDSE23_HM_recommedation/flask/app/module/data/default_show.parquet',engine='pyarrow')
