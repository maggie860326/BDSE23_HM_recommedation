from flask import Flask, render_template, request

from load_model import rec_model,rec_model_several
est = rec_model()


app = Flask(__name__)

@app.route('/')
def main():
	return render_template('rec.html')

@app.route('/', methods=['POST','GET'])
def result():
     if request.method == 'POST':
         user = request.values['user']

         rec_list,iid_list = rec_model_several(user)

         return render_template('rec.html', 
         						 user = user,
         		                 rec_list=rec_list,
         		                 iid_list = iid_list)

if __name__ == '__main__':
     app.run(host='127.0.0.1', port=8000)