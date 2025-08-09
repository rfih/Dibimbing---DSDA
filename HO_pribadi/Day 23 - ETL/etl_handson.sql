-- Extract (E)
select * from example_client_balance ecb
select * from example_client_transaction ect
limit 5
-- table : example_client_balance
-- customer_id : nilai unik -> tbc
-- first_name, last_name : nama user (ada huruf besar di awal kata) -> coba pake lower
-- city : nama2 kota dengan huruf besar di awal kata -> coba pake lower
-- gender : belum seragam -> Male, male, M, Female, F
-- initial_balance : numerik
-- nationality : nama2 negara, huruf belum standar -> JPN, Indonesia, indonesia, INA, Denmark, denmark, china


-- table : example_client_transaction
-- customer_id : nilai unik -> tbc
-- total_transactions, total_success_transactions, total_topup, total_debit : numerikal

-- Perhitungan matematis
-- final_balance = initial_balance - total_debit + total_topup
-- total_transactions dan total_success_transactions -> total_success_transactions/total_transactions (success_rate)
-- failed_transactions = total_transactions - total_success_transactions

select distinct(total_debit) from example_client_transaction ecb 
order by total_debit desc

-- Transform : dari hasil ekstraksi kita ambil kolom2 yg informatif sesuai case kita dan kita lakukan cleaning
select ecb.customer_id,
	lower(first_name),
	lower(city),
	case when lower(gender) in ('male','m') then 'L'
		when lower(gender) in ('female','f') then 'P'
	end as gender_normalize,
	case when nationality  in ('Indonesia','indonesia','INA') then 'indonesia'
		when nationality in ('denmark','Denmark') then 'denmark'
		when nationality in ('china') then 'china'
		when nationality in ('JPN') then 'japan'
	end as nationality,
	total_debit,
	total_topup,
	initial_balance - total_debit + total_topup as final_balance,
	total_transactions - total_success_transactions as failed_transactions,
	round(total_success_transactions / total_transactions :: numeric, 3) as success_rate
from example_client_balance ecb 
left join example_client_transaction ect 
on ecb.customer_id = ect.customer_id

--case 
--    when lower(coalesce(gender, 'm')) in ('male', 'm') then 'L'
--    when lower(coalesce(gender, 'm')) in ('female', 'f') then 'P'
--end as gender_normalize

-- load (initial load) -> hasil E dan T dimasukkan kedalam 1 table yg sama -> single source :
create table final_balance_client as
select ecb.customer_id,
	first_name,
	city,
	case when gender in ('male','M','Male') then 'Male'
		when gender in ('Female','F') then 'Female'
		end as gender,
	case when nationality  in ('Indonesia','indonesia','INA') then 'indonesia'
		when nationality in ('denmark','Denmark') then 'denmark'
		when nationality in ('china') then 'china'
		when nationality in ('JPN') then 'japan'
		end as nationality ,
	total_debit,
	total_topup,
	initial_balance - total_debit + total_topup as final_balance,
	total_transactions - total_success_transactions as failed_transactions,
	round(total_success_transactions / total_transactions :: numeric, 3) as success_rate
from example_client_balance ecb 
left join example_client_transaction ect 
on ecb.customer_id = ect.customer_id

-- final table
select * from final_balance_client fbc 
limit 5

-- ELT :
create table tbl_elt_final_balance as
select ecb.customer_id,
	first_name,
	city,
	gender,
	nationality ,
	total_debit,
	total_topup,
	total_success_transactions,
	total_transactions
from example_client_balance ecb 
left join example_client_transaction ect 
on ecb.customer_id = ect.customer_id


