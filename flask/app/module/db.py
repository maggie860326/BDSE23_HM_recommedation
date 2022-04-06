import pymysql

class DatabaseConnection:
    
    def __init__(self,host,user,password,db,charset='utf8',port=3306):
        self.db_settings = {
            "host": host, # "172.22.33.44"
            "port": port,
            "user": user, # "root"
            "password": password, # "root"
            "db": db, # "HM"
            "charset": charset
        }

    def read_table(self, table_name):
        try:
            # 建立Connection物件
            conn = pymysql.connect(**self.db_settings)
            # 建立Cursor物件
            with conn.cursor() as cursor:
            #資料表相關操作
                command = "SELECT * FROM "+table_name
                cursor.execute(command)
                result = cursor.fetchall()
                return result
        except Exception as ex:
            print(ex)

    def read_article_name(self, article_id):
        try:
            # 建立Connection物件
            conn = pymysql.connect(**self.db_settings)
            # 建立Cursor物件
            with conn.cursor() as cursor:
            #資料表相關操作
                command = f"SELECT prod_name FROM articles WHERE article_id={article_id}"
                cursor.execute(command)
                result = cursor.fetchone()
                # print(result[0])
                return result[0]
            
        except Exception as ex:
            print(ex)

			
			