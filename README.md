# BDSE23_HM_recommendation

## 專題簡介
此為資展國際巨量資料分析就業養成班中壢第23期（BDSE23）第四組的專題作品。
目標為利用 H&M 的顧客購買紀錄製作個人化推薦系統，並部署到網頁中呈現。

- 資料來源: [Kaggle - H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations)

- 叢集架構：本專題中使用的 Hadoop 叢集使用 7 台實體主機（共 16 台虛擬機），共 24 顆 CPU 和 84G 的 memory。

## 模型介紹
- SVD (model/surprise_svd.ipynb)
  - SVD模型同時考量顧客與產品的關係，並透過矩陣分解萃取出重要的顧客及產品特徵向量，以此來做個人化商品推薦。
  - 使用 Nicolas/surprise 套件做 SVD 模型建置，訓練的參數有factor,iteration,regulation，模型指標使用 map@k 及 rmse 兩個指標。

- KNN 
  - 以產品為基礎的推薦演算法(Item-based recommendation)。
  - 找出哪些商品背後的購買客群重疊性高，以此推薦相似商品。


## 模型調參 Spark
- 利用 Spark on Yarn 的 pandas_udf 執行 training，找出 SVD 的最佳參數組合與訓練集長度。

## 網頁設計 Flask
-推薦功能開發：
依照使用者id，並透過 SVD pkl file 預測每個使用者對於各產品的評分，拉出前12名產品，並拉取照片路徑呈現在前端網頁上。

-歷史清單功能開發：
依照使用者id ，並透過歷史交易資料篩選出顧客歷史購買資料，並拉取照片路徑呈現在前端網頁。

-自動化報表開發：
依照網站使用者輸入的年月篩選歷史訂單數據，產生匯總報表與圖形呈現在前端網頁上。

## 應用部署 Docker Compose
