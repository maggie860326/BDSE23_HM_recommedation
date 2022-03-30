from flask import Flask,render_template,request,url_for
from load_model import rec_model_several,rec_model_several_dict
from load_cus_art_mapping import load_cus_art_mapping
import os 

article_df,customer_df,trans_df = load_cus_art_mapping()
app = Flask(__name__)

@app.route('/')
def main():
	return render_template('rec.html')

### show imgs on web 
#app.config['UPLOAD_FOLDER'] = os.path.join('static', 'imgs')

@app.route('/', methods=['POST','GET'])
def result():
	if request.method =='POST':
		user = request.values['user']
		
		### cust history list 
		trans_df_filter = trans_df[trans_df['customer_id'].isin([user])]
		### cust rec list
		est_list,rec_list,iid_list = rec_model_several(user)
		predict_dict = rec_model_several_dict(user)

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
	return render_template('rec.html', 
							 user = user,
							 predict_dict=predict_dict,
							 trans_tables= trans_df_filter[['article_id']].values.tolist(),
							 user_image = img_file_his,
							 user_img = img_file)

if __name__ == '__main__':
     app.run(host='127.0.0.1', port=8000)