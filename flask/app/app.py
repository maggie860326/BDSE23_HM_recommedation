from flask import Flask,render_template,request,url_for,redirect
import sys
import os 
from module.Kfunc import recom_knn
from module.db import DatabaseConnection
from module.grid_view import *
from module.main_page import mainPage


### relative path
module_path = os.path.join('module')
sys.path.append(module_path)
import load_model 
import load_cus_art_mapping

main_page = mainPage()
app = Flask(__name__)
db = DatabaseConnection("172.22.33.44", "root", "root", "HM")

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

@app.route('/report')
def report():
    year = request.args.get('year')
    print(year)
    month = request.args.get('month')
    print(month)
    article_id = request.args.get('article_id')
    print(article_id)
    bi_df_filter = bi_df[bi_df['article_id'].isin([article_id])]
    return render_template('report.html',
                            bi_df_col=bi_df.columns,
                            bi_df = bi_df.head(5))
    
if __name__ == '__main__':
     app.run(host='127.0.0.1', port=8000,debug=True)
