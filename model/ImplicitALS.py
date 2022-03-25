import numpy as np
import pandas as pd
import implicit
from scipy.sparse import coo_matrix
from implicit.evaluation import mean_average_precision_at_k

class ImplicitALS():
    def __init__(self):
        self=self


    def data_preprocess(self,transactions,customers,articles):
        """傳入transaction,customers,articles 的 DataFrame，接著取出完整的users和items清單，然後將customer_id和article_id轉為編號，並且map到transaction上形成新的欄位。

        Args:
            transactions ([pandas DataFrame])
            customers ([pandas DataFrame])
            articles ([pandas DataFrame])
            
        Returns:
            transactions ([pandas DataFrame])
        """    
        dfu = customers
        dfi = articles
        self.ALL_USERS = dfu['customer_id'].unique().tolist()
        self.ALL_ITEMS = dfi['article_id'].unique().tolist()

        user_ids = dict(list(enumerate(self.ALL_USERS)))
        item_ids = dict(list(enumerate(self.ALL_ITEMS)))

        user_map = {u: uidx for uidx, u in user_ids.items()}
        item_map = {i: iidx for iidx, i in item_ids.items()}
        # 將落落長的使用者id和商品id轉為編號
        transactions['user_id'] = transactions['customer_id'].map(user_map)
        transactions['item_id'] = transactions['article_id'].map(item_map)

        del dfu, dfi
        return transactions
        
    def to_user_item_coo(self,df):
        """將DataFrame df 中的user_id和item_id欄位取出，並轉換為 COO sparse items x users matrix

        Args:
            df ([pandas DataFrame])

        Returns:
            [coo_matrix]: coo_matrix
        """        
        row = df['user_id'].values
        col = df['item_id'].values
        data = np.ones(df.shape[0])
        coo = coo_matrix((data, (row, col)), shape=(len(self.ALL_USERS), len(self.ALL_ITEMS)))
        return coo

    def get_val_matrices(self,data_train, data_val):
        """Create various matrices
            
            Returns a dictionary with the following keys:
                coo_train: training data in COO sparse format and as (users x items)
                csr_train: training data in CSR sparse format and as (users x items)
                csr_val:  validation data in CSR sparse format and as (users x items)
        
        """
        coo_train = self.to_user_item_coo(data_train)
        coo_val = self.to_user_item_coo(data_val)

        csr_train = coo_train.tocsr()
        csr_val = coo_val.tocsr()
        
        return {'coo_train': coo_train,
                'csr_train': csr_train,
                'csr_val': csr_val
            }


    def validate(self,matrices, factors=200, iterations=20, regularization=0.01, show_progress=False):
        """ Train an ALS model with <<factors>> (embeddings dimension) 
        for <<iterations>> over matrices and validate with MAP@12
        """
        coo_train, csr_train, csr_val = matrices['coo_train'], matrices['csr_train'], matrices['csr_val']
        
        model = implicit.als.AlternatingLeastSquares(factors=factors, 
                                                    iterations=iterations, 
                                                    regularization=regularization, 
                                                    random_state=42)
        model.fit(coo_train, show_progress=show_progress)
        
        # The MAPK by implicit doesn't allow to calculate allowing repeated items, which is the case.
        # TODO: change MAP@12 to a library that allows repeated items in prediction
        map12 = mean_average_precision_at_k(model, csr_train, csr_val, K=12, show_progress=show_progress, num_threads=0)
        # print(f"Factors: {factors:>3} - Iterations: {iterations:>2} - Regularization: {regularization:4.3f} ==> MAP@12: {map12:6.5f}")
        return map12

    # 記得改名字，function 的引數不用改
    def train_ALS(self, train_data, val_data, train_period, val_period, stride, start_val):
        
        # ========把資料轉換成model可以用的形式======================
        matrices = self.get_val_matrices(train_data, val_data)
        coo_train, csr_train, csr_val = matrices['coo_train'], matrices['csr_train'], matrices['csr_val']
        # =========================================================
        scores = pd.DataFrame()
        # ========想調的參數都寫成for迴圈============================
        for factors in [25, 50, 100, 200]:
            for iterations in [3, 10, 20]:
                for regularization in [0.01]:
                # =================================================
                
                    # ========= train model並取得準確度分數(map, rmse, mae) ===========================
                    model = implicit.als.AlternatingLeastSquares(factors=factors, 
                                                    iterations=iterations, 
                                                    regularization=regularization, 
                                                    random_state=42)
                    model.fit(coo_train, show_progress=False)
                    map12 = mean_average_precision_at_k(model, csr_train, csr_val, K=12, show_progress=False, num_threads=0)
                    # rmse = 
                    # mae = 
                    # ================================================================================
                    newRow = {
                        'train_period':train_period, 
                        'val_period':val_period, 
                        'stride':stride, 
                        'start_val':start_val,
                        # =====填寫參數名稱===============
                        'factors':factors, 
                        'iterations':iterations, 
                        'regularization':regularization, 
                        # ===============================
                        'map12':map12,
                        # 'rmse':rmse,
                        # 'mae':mae
                        }
                    print(newRow)
                    newDF = pd.DataFrame([newRow])
                    scores = pd.concat([scores, newDF], axis=0 ,ignore_index=True)

        return scores          