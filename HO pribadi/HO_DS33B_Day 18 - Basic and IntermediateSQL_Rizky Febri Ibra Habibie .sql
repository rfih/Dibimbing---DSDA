insert into mahasiswa (nim, name, tinggi_badan)
values
	(123, 'Calvin', 175),
	(124, 'Indah', 164),
	(125, 'Habibie', 200);

-- IN, AND, OR
select *
from mahasiswa
where name = 'Habibie'
	or name = 'Calvin';

select *
from mahasiswa
where name in ('Habibie', 'Calvin');

select *
from mahasiswa
where name in ('Habibie', 'Calvin')
	and tinggi_badan >= 180;

--BETWEEN
select *
from mahasiswa
where tinggi_badan between 170 and 180;

--LIKE
select *
from mahasiswa
where name like '%i%';

-- ngambil data mahasiswa mengandung huruf vokal a i e o u
SELECT *
FROM mahasiswa
WHERE name LIKE '%a%'
   OR name LIKE '%e%'
   OR name LIKE '%i%'
   OR name LIKE '%o%'
   OR name LIKE '%u%';

--huruf gede
select
	nim,
	name
from mahasiswa
where lower(name) like '%i%';

--IS NULL
insert into mahasiswa (nim, name)
values
	(126, 'Muhammad');

select *
from mahasiswa
where tinggi_badan is null;

--NOT
select * from mahasiswa
where tinggi_badan is not null;

--LIMIT
select *
from mahasiswa
limit 1;

--UPDATE
select * from mahasiswa;

update mahasiswa
set tinggi_badan = 182
where nim = 123;

--DELETE data
delete from mahasiswa
where nim = 126;

-- raw (aplikasi) --> data jelek
-- data staging (data belum diformat)
-- data warehouse --> data yang udah dibersihkan
-- data mart --> data agregasi sesuai kebutuhan

create database dvdrental;

-- ADVANCED DML (cek berapa staff yang handle payment)
select distinct staff_id
from payment;

-- tarikin list customer id yang dilayani oleh staff_id = 1
select distinct customer_id, staff_id 
from payment
where staff_id = 1 ;

-- ORDER  BY
select *
from film
order by title desc;

select * from payment
order by staff_id asc, customer_id  desc;

select 
from
where
order by

--tarikin data payment oleh customer id599 yang pembayarannya dibawah 3 dollar dan descending
select * 
from payment
where amount < 3.00
	and customer_id = 599
order by amount desc

--GROUP BY
select
	staff_id,
	COUNT(distinct customer_id) num_customer,
	SUM(amount) total_amount,
	AVG(amount) average_amount,
	MIN(amount) minimal_amount,
	MAX(amount) maximal_amount
from payment
group by staff_id, customer_id;

-- ingin tau setiap customer ngelakuin berapa banyak rental dibulab may 2005
select 
	customer_id,
	count(distinct rental_id) num_rental
from rental
where rental_date between '2005-05-01' and '2005-05-30'
group by 1;

select * from rental;

-- jika mau operasikan agregasi didalam (hasil dari count) harus setelah group by
select 
	customer_id,
	count(distinct rental_id) num_rental
from rental
where rental_date between '2005-05-01' and '2005-05-30'
group by 1
having count(distinct rental_id) > 1
order by num_rental ASC;

-- staff id mana yang melayani lebih dari 300 customer
select 
	staff_id,
	count(distinct customer_id) sum_customer
from rental
group by 1
having count(distinct customer_id)>300;

--Join
select * from film_actor;
select * from film;

select 
	fa.actor_id,
	fa.film_id,
	f.title,
	f.description
from film_actor fa
inner join film f
	on fa.film_id = f.film_id;

-- left join
select 
	fa.actor_id,
	fa.film_id,
	f.title,
	f.description
from film_actor fa
left join film f
	on fa.film_id = f.film_id
where f.film_id is null;


-- staff id mana yang nglayanin lebih dari 300 customer? munculin staff name juga
select
	r.staff_id,
	s.first_name,
	s.last_name,
	count(distinct r.customer_id) num_customer
from rental r
left join staff s
	on r.staff_id = s.staff_id
group by r.staff_id, s.first_name, s.last_name
having count(distinct r.customer_id) > 300;

--UNION
select
	'CASE 1' case,
	*

from rental
where staff_id = 1
	and customer_id = 599
	
union

select
	'CASE 2' case,
	*
	
from rental
where staff_id = 1
	and customer_id = 599;

--CASE


