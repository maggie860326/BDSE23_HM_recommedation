from flask import Flask,render_template,request,url_for
import sys
import os 
from module.Kfunc import recom_knn

### relative path
module_path = os.path.join('module')
sys.path.append(module_path)
import load_model 
import load_cus_art_mapping


article_df,customer_df,trans_df,bi_df = load_cus_art_mapping.load_cus_art_mapping()
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
    url_id = request.args.to_dict().popitem()
    url_id = url_id[0].split("\\")
    art_id = url_id[3][1:-4] # 從URL取得商品ID

    klist = recom_knn(int(art_id))




    print("#####################",type(art_id),"#######################")
    print("#####################",art_id,"#######################")
    return render_template('shop.html')


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
     app.run(host='127.0.0.1', port=8000)