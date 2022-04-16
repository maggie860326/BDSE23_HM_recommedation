# BDSE23_HM_recommendation

# 專題介紹

# 叢集架構 Hadoop

# 模型介紹 SVD & KNN
SVD模型(model/surprise_svd.ipynb)
使用 Nicolas/surprise 套件做SVD模型建置，訓練的參數有factor,iteration,regulation，模型指標使用map@k 及 rmse 兩個指標。

# 模型調參 Spark

# 網頁設計 Flask
-推薦功能開發：
依照使用者id，並透過 SVD pkl file 預測每個使用者對於各產品的評分，拉出前12名產品，並拉取照片路徑呈現在前端網頁上。

-歷史清單功能開發：
依照使用者id ，並透過歷史交易資料篩選出顧客歷史購買資料，並拉取照片路徑呈現在前端網頁。

-自動化報表開發：
依照網站使用者輸入的年月篩選歷史訂單數據，產生匯總報表與圖形呈現在前端網頁上。

# 應用部署 Docker Compose
