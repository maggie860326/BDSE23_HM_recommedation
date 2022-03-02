class implicit_ALS_model(object):
    def __init__(self, customers,articles):
        
    def 
        ALL_USERS = dfu['customer_id'].unique().tolist()
        ALL_ITEMS = dfi['article_id'].unique().tolist()

        user_ids = dict(list(enumerate(ALL_USERS)))
        item_ids = dict(list(enumerate(ALL_ITEMS)))

        user_map = {u: uidx for uidx, u in user_ids.items()}
        item_map = {i: iidx for iidx, i in item_ids.items()}

        df['user_id'] = df['customer_id'].map(user_map)
        df['item_id'] = df['article_id'].map(item_map)

        del dfu, dfi
                                            
    def to_user_item_coo(data, user_column, item_column):
        """
        Turn a dataframe with transactions into a COO sparse items x users matrix

        Args:
            data ([pandas.DataFrame]): [description]
            user_column ([pandas.Series]): [description]
            item_column ([pandas.Series]): [description]

        Returns:
            [type]: [description]
        """    
        row = user_column.values
        col = item_column.values
        ones = np.ones(data.shape[0])
        coo = coo_matrix((ones, (row, col)), shape=(len(ALL_USERS), len(ALL_ITEMS)))
        return coo

    def get_val_matrices(df_train, df_val, validation_days=7):
        """ Split into training and validation and create various matrices
            
            Returns a dictionary with the following keys:
                coo_train: training data in COO sparse format and as (users x items)
                csr_train: training data in CSR sparse format and as (users x items)
                csr_val:  validation data in CSR sparse format and as (users x items)
        
        """
        coo_train = to_user_item_coo(df_train)
        coo_val = to_user_item_coo(df_val)

        csr_train = coo_train.tocsr()
        csr_val = coo_val.tocsr()
        
        return {'coo_train': coo_train,
                'csr_train': csr_train,
                'csr_val': csr_val
            }


    def validate(matrices, factors=200, iterations=20, regularization=0.01, show_progress=True):
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
        map12 = mean_average_precision_at_k(model, csr_train, csr_val, K=12, show_progress=show_progress, num_threads=4)
        print(f"Factors: {factors:>3} - Iterations: {iterations:>2} - Regularization: {regularization:4.3f} ==> MAP@12: {map12:6.5f}")
        return map12