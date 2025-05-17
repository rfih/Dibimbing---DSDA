-- CONCAT
select 
	title,
	description,
	concat('NEW - ', title, ' - ', description, 8) title_description
from film;

select left(title, 7) from film;

select upper(title) upper_title, 
	lower(title) lower_title
from film;

-- SUBSTRING
select 
	title,
	substring(title from 3 for 5) new_title
from film;

-- TRIM
select
	title,
	trim(title) trimmed_title
from film

select
	('  CALVIN HARTONO') actual_name,
	TRIM('  CALVIN HARTONO') trimmed_name;

-- LENGTH
select 
	title,
	length(title) title_length
from film

-- POSITION
select
	title,
	POSITION('h' in title) h_position
from film
--where lower(title) like 'adaptation%';

select
	'2025-01-01' start_date,
	'2025-05-01' end_date;

select *
from film
cross join datesub
where film_date between start_date and end_date

-- SUBSTRING
select 	
	SUBSTRING(title from 3)
from film;

-- Get first word
select
	title,
	LEFT(title, position(' ' in title)-1) first_word_title, -- -1 karena spasi setelah kata pertama ngikut
	SUBSTRING(title FROM POSITION(' ' IN title) + 1) AS second_word_title
from film;

select
	title,
	LEFT(title, position(' ' in title)-1) first_word_title, -- -1 karena spasi setelah kata pertama ngikut
	RIGHT(title, POSITION(' ' IN REVERSE(title)) - 1) AS second_word_title
from film;


-- TIMESTAMP FUNCTION
select
	rental_date,
	DATE_TRUNC('month', rental_date) rental_month,
	EXTRACT(month from rental_date) rental_month_extract,
	rental_date - interval '2 months' prev_2_months,
	AGE(return_date, rental_date) rental_to_return,
	CAST(return_date as CHAR) return_date_in_char, -- hasilnya 2 karena timestamp konvert ke string jadi begitu
	CAST(inventory_id as INT) return_inven_to_int
from rental;

select inventory_id
from rental;

-- gimana caranya ngequery rental_to_return jadi 'n days' aja
select 
	AGE(date(return_date), date(rental_date)) rental_to_return
from rental;



-- SUBQUERY di select
select 
	payment_id,
	amount,
	(select AVG(amount) from payment) avg_amount,
	case
		when amount > (select AVG(amount) from payment) then 'Above Average'
		else 'Below Average'
	end as average_flag
from payment;

--subquery di where
select 
	payment_id,
	amount,
	(select AVG(amount) from payment) avg_amount
from payment
where amount >= (select avg(amount) from payment);


-- subquery di from
select 
	customer_id,
	sum(amount) total_amount
from payment
group by 1;

select AVG(total_amount) total_amount_per_customer
from (
	select
		customer_id,
		SUM(AMOUNT) total_amount
	from PAYMENT
	group by 1
	)
	
-- RANKING
select *,
	RANK() OVER(order by amount DESC) ranking,
	DENSE_RANK() OVER(order by amount DESC) dense_ranking,
	ROW_NUMBER() OVER(order by amount DESC) RN_ranking
from payment;

--Partition BY
select 
	customer_id,
	payment_id,
	amount,
	row_number() OVER(partition by customer_id order by amount DESC) ranking_w_customer
from payment
order by 1,3 desc;

-- cara ngefilter ranking 1 saja
select *
from(
	select
		customer_id,
		payment_id,
		amount,
		row_number() OVER(partition by customer_id order by amount DESC) ranking_w_customer
	from payment
	order by 1,3 desc
	)
where ranking_w_customer = 1;

----------------------
with summary as (
	select
		customer_id, 
		payment_id, 
		amount,
		row_number() OVER(partition by customer_id order by AMOUNT DESC) RANKING_W_CUSTOMER
	from payment
	order by 1,3 desc
), 
total_per_customer as (
	select
		customer_id,
		SUM(amount) total_amount
	from summary
	group by 1
)
select avg(total_amount) avg_spending_per_customer from total_per_customer;

-- RANKING
select 
	*,
	RANK() OVER(order by amount desc, payment_date DESC) RANKING,
	DENSE_RANK() OVER(order by amount desc, payment_date  DESC) DENSE_RANKING,
	ROW_NUMBER() OVER(order by amount desc, payment_date DESC) RN_ranking
from payment;


