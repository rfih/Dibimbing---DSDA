-- 1. Membuat Database dan Tabel

create database dibimbing;

create table student (
	id INT primary KEY,
	nama varchar,
	institute varchar,
	berat_badan float,
	tinggi_badan float
);

insert into student (id, nama, institute, berat_badan, tinggi_badan)
values
	(110, 'Astuti', 'ITB', 56, 163),
	(111, 'Bastomi', 'UGM', 70, 174),
	(112, 'Charlie', 'NUS', 63, 166),
	(113, 'Antony', 'Betis', 69, 177),
	(114, 'Yamal', 'Barca', 70, 180);


-------------------------------------------------------------------------

--- 2. Query Data pada Skema dvdrental

-- Tampilkan first_name dan last_name dari aktor yang memiliki first_name "Jennifer", "Nick", atau "Ed".
select *
from actor
where first_name in ('Jennifer', 'Nick', 'Ed');

-- Hitung total pembayaran (amount) untuk setiap payment_id yang totalnya lebih dari 5.99.
select 
	payment_id,
	amount
from payment
where amount > 5.99;

select
	payment_id,
	SUM(amount) total_amount
from payment
where amount > 5.99
group by 1;

-- Kelompokkan film berdasarkan durasi menjadi 4 kategori:
--Over 100 menit
--87-100 menit
--72-86 menit
--Under 72 menit

select
	film_id,
	title,
	case
		when length > 100 then 'Over 100 menit'
		when length >= 87 then '87-100 menit'
		when length >= 72 then '72-86 menit'
		when length < 72 then 'Under 72 menit'
	end as length_category
from film;

-- Gabungkan data dari tabel rental dan payment untuk menampilkan rental_id, rental_date, payment_id, dan amount, urutkan berdasarkan amount secara ascending.
select *
from rental;

select *
from payment;

select 
	r.rental_id,
	r.rental_date,
	p.payment_id,
	p.amount
from rental r
inner join payment p
	on r.rental_id = p.rental_id
order by amount asc;

-- Gunakan UNION untuk menggabungkan alamat (address) yang memiliki city_id = 42 dengan city_id = 300.
select * from city;
select * from address;

select
	*
from address
where city_id = 300
union
select
	*
from address
where city_id = 42;


	
