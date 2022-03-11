# create table:selling_data
CREATE TABLE HM.selling_data (
    t_dat varchar(555),
    customer_id varchar(255),
    article_id varchar(255),
    price varchar(255),
    sales_channel_id varchar(255),
    y varchar(255),
    m varchar(255),
    d varchar(255),
    order_id varchar(255)
);

# insert data into selling_data table 
insert into HM.selling_data(t_dat,customer_id,article_id,price,sales_channel_id,y,m,d,order_id)
	SELECT *, 
		   SUBSTR(t_dat,1, 4) as y,
		   SUBSTR(t_dat,6, 2) as m,
		   SUBSTR(t_dat,9, 2) as d,
		   concat(customer_id,article_id) as order_id
	    FROM HM.transactions_train limit 100;

SELECT * FROM HM.selling_data;

# bi report 
select y,
       count(customer_id) as customer_cnt,
       count(article_id) as article_cnt,
       sum(price) as revenue,
       count(order_id) as order_cnt
	from HM.selling_data
group by y;













