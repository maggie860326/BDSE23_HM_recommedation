# create table by sql query
create TABLE HM.cust_art_list(
    customer_id varchar(255),
    article_id varchar(255));

insert into HM.cust_art_list(customer_id,article_id)
	select customer_id,
       article_id 
from HM.transactions_train;