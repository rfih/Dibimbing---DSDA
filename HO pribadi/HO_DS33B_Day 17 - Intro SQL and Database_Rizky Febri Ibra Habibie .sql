-- DDL (Data Definition Language)
create table mahasiswa (
	nim INT primary KEY,
	name varchar,
	tinggi_badan float
);

drop table mahasiswa;



-- DATA TYPES
--string, integer, date, datetime, boolean
--ctrl + /

-- STRING - - > CHAR, VARCHAR
--char untuk kolom yang sudah fix, contoh gender: F, M
--VARCHAR yang variatif

alter table mahasiswa 
add column berat_badan INT;

alter table mahasiswa
drop column tinggi badan;

alter table mahasiswa 
rename column name to nama_lengkap;

alter table mahasiswa
alter column nama_lengkap set not null;

alter table mahasiswa 
rename to mahasiswa_oxford;

--ngosongin table
truncate table mahasiswa_oxford;

drop table mahasiswa_oxford;

insert into mahasiswa (nim, name, tinggi_badan)
values
	(123, 'Calvin', 175),
	(124, 'Indah', 164),
	(125, 'Habibie', 200);

select *
from mahasiswa;

insert into mahasiswa (nim, name, tinggi_badan)
values
	(123, 'Calvin', 175),
	(124, 'Indah', 164),
	(125, 'Habibie', 200);