import os
import module.load_model as load_model
from module.load_cus_art_mapping import *
from module.grid_view import *
import os

class mainPage():
    def __init__(self) -> None:
        article_df,customer_df,self.trans_df,bi_df = load_cus_art_mapping()
        pass

    def get_history_and_rec_list(self,user):
        ### cust history list
        trans_df_filter = self.trans_df[self.trans_df['customer_id'].isin([user])]
        ### cust rec list
        est_list,rec_list,iid_list = load_model.rec_model_several(user)
        # predict_dict = load_model.rec_model_several_dict(user)

        ###	show history imgs on web
        img_file_his = []
        for imgs in trans_df_filter[['article_id']].values.tolist():
            img_name = '0' + str(imgs[0])+'.jpg'
            filename_test = os.path.join(os.path.join('static', 'imgs',img_name[:3]), img_name)
            img_file_his.append(filename_test)
        
        ### get recommend items' id, name and image path as a dict list
        dict_list = get_img_and_name(iid_list)

        return img_file_his, dict_list