-- WIndows function
select 
	payment_id,
	amount,
	staff_id,
	SUM(amount) OVER(partition by staff_id) as total_sales_by_staff
from payment;

select 
	payment_date,
	payment_id,
	customer_id,
	amount,
	LAG(amount) OVER(partition by customer_id order by payment_date) as prev_payment_amount
from payment;

-- jika 2 payment sebelumnya
select 
	payment_date,
	payment_id,
	customer_id,
	amount,
	lag(amount) over(partition by customer_id order by payment_date)
	as prev_payment_amount,
	lag(amount, 2) over(partition by customer_id order by payment_date)
	as prev_payment_amount_2 -- melihat transaksi sebelumnya
from payment;
--
select
	x.*,
	lag(x.prev_payment_amount) over (partition by x.customer_id order by x.payment_date) as prev_payment_amount_twostep
from
(select
	payment_date,
	payment_id,
	customer_id,
	amount,
	lag(amount) over (partition by customer_id order by payment_date) as prev_payment_amount --sebelum
from payment p) x;
--
with raw as ( -- raw sebagai variabel sementara, didefine lagi dibawah
	select 
		payment_date,
		payment_id,
		customer_id,
		amount,
		LAG(amount) OVER(partition by customer_id order by payment_date) as prev_payment_amount
	from payment
)
select
	x.*,
	lag(x.prev_payment_amount) over (partition by x.customer_id order by x.payment_date) as prev_payment_amount_twostep
from raw x;

-- running total
select DISTINCT
	DATE(payment_date) payment_date,
	SUM(amount) OVER(order by DATE(PAYMENT_DATE) asc) as total_sales_by_staff
from PAYMENT
order by 1 ASC;

-- Moving Average
with summary as (
	select
	date(payment_date) payment_date,
	SUM(amount) total_sales
	from payment p group by 1
	order by 1
)
select
	payment_date,
	total_sales,
	SUM(total_sales) over(order by payment_date) running_total,
	AVG(total_sales) over(order by payment_date rows between 2 preceding and current row) ma3
from summary
group by 1,2;


--- Case Study Sample Supperstore
-- understanding the data
--1. lihat struktur table
select *
from sample limit 5;

-- 2. cek jumlah row
select
	count(*)
from sample;

-- 3. ada missing value dikolom penting ga?
select 
	COUNT(*) - COUNT('Order ID') as missing_order_id,
	COUNT(*) - COUNT('Customer ID') as missing_customer_id,
	COUNT(*) - COUNT('Sales') as missing_sales
from sample limit 10;

--
select
	*
from sample s
where "Row ID" IS NULL
  and "Order ID" IS NULL
  and "Order Date" IS NULL
  and "Ship Date" is null;

--
select
  COUNT(*) FILTER (WHERE 'Order ID' IS NULL) AS null_order_id,
  COUNT(*) FILTER (WHERE 'Customer ID' IS NULL) AS null_customer_id,
  COUNT(*) FILTER (WHERE 'Product ID' IS NULL) AS null_product_id
from sample;

-- cek duplication
select 	
	"Order ID",
	"Customer ID",
	"Product ID",
	"Row ID",
	ROW_NUMBER() over (partition by "Order ID", "Customer ID", "Product ID" order by "Order Date") rank
from sample
group by 1,2,3,4, "Order Date" 
order by 5 DESC;

--cek berdasarkan row
select distinct "Row ID"
from(select 	
		"Order ID",
		"Customer ID",
		"Product ID",
		"Row ID",
		ROW_NUMBER() over (partition by "Order ID", "Customer ID", "Product ID" order by "Order Date") rank
	from sample
	group by 1,2,3,4, "Order Date" 
	order by 5 DESC
)
where rank = 2;

-- remove duplication
delete from sample
where "Row ID" in (
	select distinct "Row ID"
		from (
			select
				"Order ID",
				"Customer ID",
				"Product ID",
				"Row ID",
				ROW_NUMBER() over (partition by "Order ID", "Customer ID", "Product ID" order by "Order Date") rank
			from sample
			group by 1,2,3,4, "Order Date"
			order by 5 desc
			)
		where rank = 2
); --cek lagi apakah masih ada duplikasi dengan run query sebelumnya

-- EDA 1 : Berapa total pendapatan dan keuntungan?
select 	
	--DATE_TRUNC('Month', date("Order Date")) order_month, tidak bisa pake DATE_TRUNC karena format timestamp disini menggunakan '/' harus di rubah format dulu
	"Order Date",
	SUM("Sales") total_pendapatan,
	SUM("Profit") total_keuntungan,
	SUM("Profit")/SUM("Sales") percent_profit
from sample
group by 1;

-- EDA 2: Produk apa yang paling populer?
select 	
	"Product ID",
	"Product Name",
	sum("Quantity") as item_sold
from sample s 
group by 1,2
order by sum("Quantity") desc
limit 10;

-- EDA 3: Siapa 10 pelanggan dengan total pembelian terbanyak?
select 	
	"Customer ID",
	"Customer Name",
	sum("Sales") as total_sales
from sample s 
group by 1,2
order by sum("Sales") desc
limit 10;

-- EDA 4: Bulan apa yang penjualannya paling tinggi?
select to_date("Order Date", 'MM/DD/YYYY') Order_Date
from sample;

select 	
	extract(month from to_date("Order Date", 'MM/DD/YYYY')) Order_month,
	sum("Quantity") as total_penjualan
from sample s 
group by 1
order by 2 desc
limit 10;

-- EDA 5: Bagaimana trend pengjualan tiap bulannya?
select 	
	date(DATE_TRUNC('month', to_date("Order Date", 'MM/DD/YYYY'))) Order_month,
	sum("Quantity") as total_penjualan
from sample s 
group by 1
order by 1 asc;

-- EDA 6: Berapa jumlah pelanggan untuk masing-masing segmentasi berdasarkan profit?
-- profit >= 500 --> "Highly Profitable"
-- profit >= 100, <500 --> Moderate Profitable
-- else --> Not profitable
with raw as (
	select
		"Customer ID",
		sum("Profit") total_profit
	from sample
	group by 1
),
segmentation as (
	select
		"Customer ID", 
		case
			when total_profit >= 500 then 'Highly Profitable'
			when total_profit >= 100 then 'Moderate Profitable'
			else 'Not Profitable'
		end as profit_segmentation
	from raw
)
select
	profit_segmentation, count(distinct "Customer ID") num_customer
from segmentation
group by 1;

-- EDA 7: Siapa pelanggan dengan profitabilitas tertinggi?
select
	"Customer ID",
	"Customer Name",
	SUM("Profit") total_profit
from sample
group by 1,2
order by 3 desc
limit 5;

-- EDA 8: Mengidentifikasi pelangggan yang kembali berbelanja
select distinct "Customer ID", "Customer Name"
from sample s 
group by 1,2
having COUNT(distinct "Order ID") > 1;

-- EDA 9: Bagaimana hubungan sub-category dengan tren penjualan bulanan?
select
	"Sub-Category",
	date(DATE_TRUNC('MONTH', to_date("Order Date", 'MM/DD/YYYY'))) order_month,
	SUM("Quantity") total_penjualan
from sample
group by 1,2;




