create database ubuvilla;

select *
from villa_data;

-- sort price by the most expensive
select *
from villa_data
order by "Price_1" desc;

alter table villa_data
drop column price;

--rework bedroom and capacity
alter table villa_data add column bedroom_num integer;

select
  substring("Bedrooms" from '\d+$') AS bedroom_num
from villa_data;

update villa_data
set bedroom_num = cast(substring("Bedrooms" from '\d+$') as integer);


alter table villa_data add column capacity_num integer;

select
  substring("Capacity" from '\d+$') AS capacity_num
from villa_data;

update villa_data
set capacity_num = cast(substring("Capacity" from '\d+$') as integer);

-- Villas with more than 2 bedrooms
select *
from villa_data
where cast(bedroom_num as integer) > 2;

--Average price per bedroom count
select bedroom_num,
	AVG("Price_1") as avg_price
from villa_data
group by bedroom_num
order by bedroom_num desc; 

--Count villas by capacitt
select capacity_num,
	COUNT(*) as total_listings
from villa_data
group by capacity_num 
order by capacity_num desc;