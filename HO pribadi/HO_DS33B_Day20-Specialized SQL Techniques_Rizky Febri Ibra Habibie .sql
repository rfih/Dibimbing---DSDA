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