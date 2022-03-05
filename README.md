# BDSE23_HM_recommedation

# 專案介紹



# 訓練模型
1. 先將 transaction 資料表最後一星期的資料切出來當作 test data，其餘作為 train data。
2. 用 train & test 訓練不同的模型以及不同的超參數，並將訓練好的模型存成 pickle 檔和資料表。
3. 將 train data 切成 12 份，每份的最後一星期作為 validation data。
4. 調出 pickle檔