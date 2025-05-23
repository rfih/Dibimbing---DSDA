-- Tampilkan nama pelanggan yang pernah melakukan transaksi dengan jumlah lebih dari rata-rata transaksi di tabel payment
select 
	payment_id,
	amount,
	(select AVG(amount) from payment) avg_amount,
	case
		when amount > (select AVG(amount) from payment) then 'Above Average'
		else 'Below Average'
	end as average_flag
from payment;

-- Ambil daftar film yang memiliki durasi lebih panjang dibandingkan durasi rata-rata dari semua film dalam tabel film.
select 
	film_id,
	title,
	length,
	(select AVG(length) from film) avg_length,
	case
		when length > (select AVG(length) from film) then 'Above Average'
		else 'Below Average'
	end as average_flag
from film
order by 2 asc;

-- Buat query untuk menampilkan aktor yang hanya membintangi satu film dalam database.
select 
	actor_id,
	first_name,
	last_name
from actor
where actor_id in (
				select actor_id
				from film_actor
				group by actor_id 
				having count (film_id) = 1);
-- Check
select
	a.actor_id,
	a.first_name,
	a.last_name,
	COUNT(fa.film_id) film_count
FROM actor a
JOIN film_actor fa 
	ON a.actor_id = fa.actor_id
GROUP by
	a.actor_id, 
	a.first_name,
	a.last_name
ORDER BY film_count asc;

-- Gunakan RANK() untuk menentukan peringkat film berdasarkan rental_rate.
select *,
	RANK() OVER(order by rental_rate DESC) ranking
from film;

-- Gunakan DENSE_RANK() untuk menentukan peringkat pelanggan berdasarkan total transaksi yang mereka lakukan.
select 
	c.customer_id,
	c.first_name,
	c.last_name,
	COUNT(c.customer_id) as total_transaction,
	DENSE_RANK() OVER(order by COUNT(c.customer_id) DESC) transaction_rank
from customer c
join payment p on c.customer_id = p.customer_id
group by 1,2,3
order by transaction_rank;

-- Gunakan ROW_NUMBER() untuk memberikan nomor urut pada daftar film berdasarkan release_year.
select *,
	ROW_NUMBER() OVER(order by release_year DESC) RN_ranking
from film;

-- Gunakan CTE untuk membuat daftar pelanggan yang melakukan transaksi lebih dari 10 kali.
WITH transaction_count AS (
    SELECT 
        customer_id,
        COUNT(payment_id) AS total_transactions
    FROM payment
    GROUP BY customer_id
)
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    tc.total_transactions
FROM transaction_count tc
JOIN customer c ON c.customer_id = tc.customer_id
WHERE tc.total_transactions > 10
ORDER BY tc.total_transactions DESC;

-- Gunakan CTE untuk mendapatkan daftar film dengan jumlah rental terbanyak.
WITH film_rental_count AS (
    SELECT 
        i.film_id,
        COUNT(r.rental_id) AS rental_count
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    GROUP BY i.film_id
)
SELECT 
    f.film_id,
    f.title,
    frc.rental_count
FROM film_rental_count frc
JOIN film f ON f.film_id = frc.film_id
ORDER BY frc.rental_count DESC;

--Buat query yang mengelompokkan film berdasarkan rental_rate:
--Jika rental_rate lebih dari 4, kategori "Premium"
--Jika rental_rate antara 2 dan 4, kategori "Regular"
--Jika rental_rate kurang dari 2, kategori "Budget"
SELECT 
    film_id,
    title,
    rental_rate,
    CASE 
        WHEN rental_rate > 4 THEN 'Premium'
        WHEN rental_rate BETWEEN 2 AND 4 THEN 'Regular'
        WHEN rental_rate < 2 THEN 'Budget'
    END AS rental_category
FROM film
ORDER BY rental_rate DESC;


--Buat query yang mengelompokkan pelanggan berdasarkan total transaksi mereka:
--Pelanggan dengan total transaksi lebih dari $100 sebagai "High Value Customer"
--Pelanggan dengan transaksi antara $50-$100 sebagai "Medium Value Customer"
--Pelanggan dengan transaksi di bawah $50 sebagai "Low Value Customer"
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(p.amount) AS total_transaction,
    CASE 
        WHEN SUM(p.amount) > 100 THEN 'High Value Customer'
        WHEN SUM(p.amount) BETWEEN 50 AND 100 THEN 'Medium Value Customer'
        WHEN SUM(p.amount) < 50 THEN 'Low Value Customer'
    END AS customer_category
FROM customer c
JOIN payment p ON c.customer_id = p.customer_id
GROUP BY 1,2,3
ORDER BY total_transaction DESC;





