from flask import Flask,render_template,request,url_for
import sys
import os 
import json
import plotly
import plotly.express as px
import pandas as pd

### relative path
module_path = os.path.join('module')
sys.path.append(module_path)
import load_model 
import load_cus_art_mapping

article_df,customer_df,trans_df,bi_df = load_cus_art_mapping.load_cus_art_mapping()
# data part
# bi_data_p = pd.read_parquet('module/data/train_one_month.parquet',engine='pyarrow')
bi_data_p = pd.read_parquet('module/data/transactions_train.parquet',engine='pyarrow')
bi_data_p['t_dat'] = pd.to_datetime(bi_data_p['t_dat'])
bi_data_p['year'] = bi_data_p['t_dat'].dt.year.astype('str')
bi_data_p['month'] = bi_data_p['t_dat'].dt.month.astype('str')


app = Flask(__name__)

@app.route('/')
def main():
	user = "00083cda041544b2fbb0e0d2905ad17da7cf1007526fb4c73235dccbbc132280"
	### cust history list
	trans_df_filter = trans_df[trans_df['customer_id'].isin([user])]
	### cust rec list
	est_list,rec_list,iid_list = load_model.rec_model_several(user)
	predict_dict = load_model.rec_model_several_dict(user)

	###	show history imgs on web
	img_file_his = []
	for imgs in trans_df_filter[['article_id']].values.tolist():
		img_name = '0' + str(imgs[0])+'.jpg'
		filename_test = os.path.join(os.path.join('static', 'imgs',img_name[:3]), img_name)
		img_file_his.append(filename_test)
	
	### show rec imgs on web using article_id 
	img_file = []
	for imgs in predict_dict:
		img_name = '0' + str(imgs[0])+'.jpg'
		filename_test = os.path.join(os.path.join('static', 'imgs',img_name[:3]), img_name)
		img_file.append(filename_test)		
		
	return render_template('index.html', 
							user = user,
							predict_dict=predict_dict,
							trans_tables= trans_df_filter[['article_id']].values.tolist(),
							user_image = img_file_his,
							user_img = img_file)

### show imgs on web 
#app.config['UPLOAD_FOLDER'] = os.path.join('static', 'imgs')

@app.route('/', methods=['POST'])
def result():
	if request.method =='POST':
		user = request.form['select1']
		print(user)
	### cust history list 
		trans_df_filter = trans_df[trans_df['customer_id'].isin([user])]
		print(trans_df_filter.head(5))
	### cust rec list
		est_list,rec_list,iid_list = load_model.rec_model_several(user)
		predict_dict = load_model.rec_model_several_dict(user)

	###	show history imgs on web
	img_file_his = []
	for imgs in trans_df_filter[['article_id']].values.tolist():
		img_name = '0' + str(imgs[0])+'.jpg'
		filename_test = os.path.join(os.path.join('static', 'imgs',img_name[:3]), img_name)
		img_file_his.append(filename_test)
	
	### show rec imgs on web using article_id 
	img_file = []
	for imgs in predict_dict:
		img_name = '0' + str(imgs[0])+'.jpg'
		filename_test = os.path.join(os.path.join('static', 'imgs',img_name[:3]), img_name)
		img_file.append(filename_test)		
	return render_template('index.html', 
							 user = user,
							 predict_dict=predict_dict,
							 trans_tables= trans_df_filter[['article_id']].values.tolist(),
							 user_image = img_file_his,
							 user_img = img_file)
							 
@app.route('/shop')
def shop():
	return render_template('shop.html')

@app.route('/report', methods=['POST','GET'])
def report():
	if request.method =='POST':
		# get request
		custid_t = request.values.to_dict()
		
		# year filter
		year = custid_t['year']
		if year =='all':
			year_f = ['2018','2019','2020']
			year_filter = bi_data_p['year'].isin(year_f)
		else:
			year_f = year
			year_filter = bi_data_p['year'].isin([year_f])
		
		# month filter
		month = custid_t['month']
		if month == 'all':
			month_f = ['1','2','3','4','5','6','7','8','9','10','11','12']
			month_filter = bi_data_p['month'].isin(month_f)
		else:
			month_f = month
			month_filter = bi_data_p['month'].isin([month_f])
		
		print(month_f)
		print(year_f)
		print(custid_t)
		
		
		#month_filter = bi_data_p['month'].isin(['8','9'])
		print(month_filter)
		filter_bi = bi_data_p[year_filter & month_filter]
		print(filter_bi.info())
		
		# group by sum price 
		groupby_df = filter_bi[['year','month','price']].groupby(['year','month'])['price'].sum().to_frame('產品總營收').reset_index()
		groupby_df.columns = ['年份','月份','產品總營收']
		groupby_df['產品總營收'] = groupby_df['產品總營收'].astype('int')
		groupby_df['年份'] = groupby_df['年份'].astype('int')
		groupby_df['月份'] = groupby_df['月份'].astype('int')
		groupby_df.sort_values(['年份','月份'], ascending=[True,True],inplace=True)
		print(groupby_df.head())
		print(groupby_df.info())
		
		# plotly line plot 
		fig = px.line(groupby_df, 
					  x = "月份", 
					  y = "產品總營收",
					  color = "年份",
					  markers = True)
					  
		figjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

		return render_template('report.html',
						bi_df_col = groupby_df.columns,
						bi_df_filter = groupby_df,
						fig=figjson)
						
	### default page ###
#	year_filter = bi_data_p['year'].isin(['2018','2019','2020'])
#	month_filter = bi_data_p['month'].isin(['1','2','3','4','5','6','7','8','9','10'])
#	filter_bi = bi_data_p[year_filter & month_filter]
#	groupby_df = filter_bi[['year','month','price']].groupby(['year','month'])['price'].sum().to_frame('產品總營收').reset_index()
#	groupby_df.columns = ['年份','月份','產品總營收']	
#	groupby_df['產品總營收'] = groupby_df['產品總營收'].astype('int')
#	groupby_df['年份'] = groupby_df['年份'].astype('int')
#	groupby_df['月份'] = groupby_df['月份'].astype('int')
#	groupby_df.sort_values(['年份','月份'], ascending=[True,True],inplace=True)
	
	# read default page dataframe
	groupby_df = pd.read_parquet('module/data/default_show.parquet',engine='pyarrow')
	groupby_df['年份'] = groupby_df['年份'].astype('object')
	groupby_df['月份'] = groupby_df['月份'].astype('object')
	
	print(groupby_df.info())
	
	# plotly line plot 
	fig = px.line(groupby_df, 
				  x = "月份", 
				  y = "產品總營收",
				  color = "年份",
				  markers = True)
				  
	figjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	
	return render_template('report.html',
							bi_df_col=groupby_df.columns,
							bi_df_filter = groupby_df.head(5),
							fig = figjson)
	
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000,debug=True)