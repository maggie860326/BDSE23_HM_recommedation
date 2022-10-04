# BDSE23_HM_recommendation

## 專題簡介
此為資展國際巨量資料分析就業養成班中壢第23期（BDSE23）第四組的專題作品。
目標為利用 H&M 的顧客購買紀錄製作個人化推薦系統，並部署到網頁中呈現。

- 資料來源：[Kaggle - H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations)

- 叢集架構：本專題中使用的 Hadoop 叢集使用 7 台實體主機（共 16 台虛擬機），共 24 顆 CPU 和 84G 的 memory。
- 詳細介紹可以參考簡報：`BDSE23 專題發表 第四組.pdf`

## 模型介紹
對應目錄：`model`
- SVD (`surprise_svd.ipynb`)
  - SVD模型同時考量顧客與產品的關係，並透過矩陣分解萃取出重要的顧客及產品特徵向量，以此來做個人化商品推薦。
  - 使用 Nicolas/surprise 套件做 SVD 模型建置，訓練的參數有factor,iteration,regulation，模型指標使用 map@k 及 rmse 兩個指標。

- KNN (`K-func.py`)
  - 以產品為基礎的推薦演算法(Item-based recommendation)。
  - 找出哪些商品背後的購買客群重疊性高，以此推薦相似商品。


## 以時間序列的交叉驗證方法對模型調參
對應目錄：`spark`

目的：在 Spark 上進行 Time series cross validation 找出最佳的 SVD 模型參數。

使用方法：
- 將 module 壓縮成 zip 檔以便讓 Spark 讀取其中的程式。
- 在終端機輸入 `submit_main.sh 天數` 令 Spark 執行 `__main__.py 天數`
- `__main__.py`：
  - 後面加上「天數」指定 training data 要以多少天為長度。
  - 內容：利用 pandas_udf 函式在 Spark 上分散式執行 Time series cross validation，並將結果（dataframe）存成 parquet 檔。

## 網頁
對應目錄：`flask/app`
- 網頁功能開發：
  - 歷史清單功能：選擇使用者id ，篩選出顧客歷史購買資料，並拉取商品照片呈現在前端網頁。
  - 個人化推薦功能 (SVD)：選擇使用者id，透過 `module/rec_svd_model.pkl` 預測該使用者對於各產品的評分，拉出前12名商品，並拉取對應商品資料與照片呈現在前端網頁。
  - 相似商品推薦功能 (KNN)：點選任意商品照片，即抓取該商品的id，透過 `module/Kfunc.py` 找出與其最接近的13樣商品，並拉取對應商品資料與照片呈現在前端網頁。
  - 自動化報表開發：依照網站使用者輸入的年月篩選歷史訂單數據，產生匯總報表與圖形呈現在前端網頁上。

- Docker Compose：
  - 包含 MySQL container 和 Flask container
