def load_cus_art_mapping():
	import mysql.connector
    
	mydb = mysql.connector.connect(
	  host="172.22.33.44",
	  user="root",
	  password="root",
	  database="HM"
	)

	mycursor = mydb.cursor()

    ### article data
	mycursor.execute("SELECT * FROM articles")

	myresult = mycursor.fetchall()

	articles_cols = ['article_id', 'prod_name','product_code','product_type_no',
	            'product_type_name','product_group_name','graphical_appearance_no','graphical_appearance_name','colour_group_code','colour_group_name',
				'perceived_colour_value_id','perceived_colour_value_name','perceived_colour_master_id','perceived_colour_master_name','department_no',
				'department_name','index_code','index_name','index_group_no','index_group_name','section_no','section_name','garment_group_no','garment_group_name','detail_desc']
	import pandas as pd			
	article_df = pd.DataFrame (myresult, columns = articles_cols)
	
	### customer data
	mycursor.execute("SELECT * FROM customers limit 1000")

	myresult2 = mycursor.fetchall()

	customers_cols = ['customer_id', 'FN','Active','club_member_status','fashion_news_frequency',
	'age','postal_code']
				
	customer_df = pd.DataFrame (myresult2, columns = customers_cols)
	
	### transactions data
	mycursor.execute("SELECT * FROM transactions_train limit 1000")

	myresult3 = mycursor.fetchall()

	trans_cols = ['t_dat','customer_id','article_id','price','sales_channel_id','price_int']
				
	trans_df = pd.DataFrame (myresult3, columns = trans_cols)

	return article_df,customer_df,trans_df
	
