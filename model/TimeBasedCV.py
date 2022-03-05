
from dateutil.relativedelta import *


class TimeBasedCV(object):
    '''
    Parameters 
    ----------
    train_period: int
        number of time units to include in each train set
        default is 30
    val_period: int
        number of time units to include in each val set
        default is 7
    freq: string
        frequency of input parameters. possible values are: days, months, years, weeks, hours, minutes, seconds
        possible values designed to be used by dateutil.relativedelta class
        deafault is days
    '''
    
    
    def __init__(self, freq='days'):
        self.freq = freq

        
        
    def split(self, data, date_column='record_date',train_period=30, val_period=7, gap=0, stride=0,show_progress=False):
        '''
        Generate indices to split data into training and val set
        
        Parameters 
        ----------
        data: pandas DataFrame
            your data, contain one column for the record date 
        date_column: string, deafult='record_date'
            date of each record
        gap: int, default=0
            for cases the val set does not come right after the train set,
            *gap* days are left between train and val sets
        stride: int, default=0
        
        
        Returns 
        -------
        train_index ,val_index: 
            list of tuples (train index, val index) similar to sklearn model selection
        '''
        
        # check that date_column exist in the data:
        try:
            data[date_column]
        except:
            raise KeyError(date_column)
                    
        train_indices_list = []
        val_indices_list = []
        
        end_val = data[date_column].max()
        start_val = end_val - eval('relativedelta('+self.freq+'=val_period)')
        end_train = start_val - eval('relativedelta('+self.freq+'=gap)')
        start_train = end_train - eval('relativedelta('+self.freq+'=train_period)')
        

        while start_train > data[date_column].min():
            # train indices:
            cur_train_indices = list(data[(data[date_column]>=start_train) & 
                                     (data[date_column]<end_train)].index)

            # val indices:
            cur_val_indices = list(data[(data[date_column]>=start_val) &
                                    (data[date_column]<end_val)].index)
            
            if(show_progress):
                print("Train period:",start_train,"-" , end_train, ", val period", start_val, "-", end_val,
                    "# train records", len(cur_train_indices), ", # val records", len(cur_val_indices))

            train_indices_list.append(cur_train_indices)
            val_indices_list.append(cur_val_indices)

            # update dates:
            end_val = end_val - eval('relativedelta('+self.freq+'=stride)')
            start_val = end_val - eval('relativedelta('+self.freq+'=val_period)')
            end_train = start_val - eval('relativedelta('+self.freq+'=gap)')
            start_train = end_train - eval('relativedelta('+self.freq+'=train_period)')

        # mimic sklearn output  
        index_output = [(train,val) for train,val in zip(train_indices_list,val_indices_list)]

        self.n_splits = len(index_output)
        
        return index_output
    
    
    def get_n_splits(self):
        """Returns the number of splitting iterations in the cross-validator
        Returns
        -------
        n_splits : int
            Returns the number of splitting iterations in the cross-validator.
        """
        return self.n_splits 
