from flask import Flask,render_template,request,url_for,redirect
import sys
import os 
from module.Kfunc import recom_knn
from module.db import DatabaseConnection
from module.grid_view import *
from module.main_page import mainPage
import pandas as pd
import json
import plotly
import plotly.express as px

### relative path
module_path = os.path.join('module')
sys.path.append(module_path)
import load_model 
import load_cus_art_mapping

main_page = mainPage()
app = Flask(__name__)
db = DatabaseConnection("172.22.33.44", "root", "root", "HM")

bi_data_p = pd.read_parquet('module/data/transactions_train.parquet',engine='pyarrow')
bi_data_p['t_dat'] = pd.to_datetime(bi_data_p['t_dat'])
bi_data_p['year'] = bi_data_p['t_dat'].dt.year.astype('str')
bi_data_p['month'] = bi_data_p['t_dat'].dt.month.astype('str')

@app.route('/')
def main():
    user = "00083cda041544b2fbb0e0d2905ad17da7cf1007526fb4c73235dccbbc132280"
    
    img_file_his, dict_list = main_page.get_history_and_rec_list(user)
    
    return render_template('index.html', 
                            user = user,
                            user_image_his = img_file_his,
                            rec_list = dict_list)


@app.route('/', methods=['POST'])
def result():
    if request.method =='POST':
        user = request.form['select1']
        print("user id: ",user)

    img_file_his, dict_list = main_page.get_history_and_rec_list(user)
    
    return render_template('index.html', 
                            user = user,
                            user_image_his = img_file_his,
                            rec_list = dict_list)
                             
@app.route('/shop')
def shop():

    # url_id = request.args.to_dict().popitem()
    # url_id = url_id[0].split("\\")
    # art_id = url_id[3][1:-4] # 從URL取得商品ID

    art_id = request.args.get("id")
    print("art_id = ", art_id)

    klist = recom_knn(int(art_id))
    for i in klist: print("KNN recommend: ",i)

    print("#####################",type(klist),"#######################")
    print(klist)
    # print("#####################",url_id,"#######################")
    # return render_template('shop.html')
    
    return redirect(url_for("show_img", list= klist, id = art_id))

@app.route('/show') ### 轉此顯示圖片或可以直接轉網頁用
def show_img():

    nlist=[]
    arg = request.args.getlist("list") # 從URL REQUEST 取出 ARGS 轉 LIST
    orig = request.args.get("id") # 取得來源商品ID
    orig_path = os.path.join("static/imgs/", "0"+str(orig)[0:2]+"/", "0"+ orig +".jpg")
    # print("path : =====>",orig_path)


    nlist = get_img_and_name(arg)


    # for i in arg: 
    #     print("arg => "+i[1:-1])## 取出ID
    #     getdb =  db.read_article_name(i[1:-1]) # 從資料庫取得商品名稱
    #     img = os.path.join("static/imgs/", "0"+i[1:3]+"/", "0"+i[1:-1]+".jpg") # 取出圖片路徑
    #     dic= {"name":getdb[0][0],"img":img,"id":i[1:-1]} # 將 圖片、名稱、ID 加入 DICT
    #     nlist.append(dic) # 製作成LIST
    print("#############",nlist,"#################")
    
    return render_template('shop.html', list = nlist, o_path = orig_path)

@app.route('/report',methods=['POST','GET'])
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
							bi_df_filter = groupby_df.head(10),
							fig = figjson)    
    
if __name__ == '__main__':
     app.run(host="0.0.0.0", port=8000,debug=True)
