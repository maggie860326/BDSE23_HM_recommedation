from module.db import DatabaseConnection

db = DatabaseConnection("172.22.33.44", "root", "root", "HM")

def get_img_and_name(article_list):
    dict_list=[]
    for id in article_list: 
        name =  db.read_article_name(id)
        img = f"static/imgs/0{str(id)[0:2]}/0{id}.jpg" 

        dic= {"name":name,"img":img,"id":id}
        dict_list.append(dic)

    return dict_list