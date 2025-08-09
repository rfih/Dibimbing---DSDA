create database netflixdb;

-- UNDERSTANDING THE DATA
select * from view_summary
limit 10;

select * from tv_show t
limit 10;
select * from movie m
limit 10;
select * from season s
limit 10;

-- CHECK DUPLICATION
select ID, COUNT(ID)
from tv_show
group by 1
having COUNT(ID) > 1;

--Film dan serial apa yang paling populer berdasarkan jumlah penonton dan total jam ditonton?

--film
select 
	movie_id,
	m.title, -- ditambah dari left join
	sum(hours_viewed) total_jam,
	sum(views) total_penonton
from view_summary vs
left join movie m -- jika ingin menambahkan title movie dari table movie
	on vs.movie_id = m.id
where movie_id is not null --exclude null
group by 1,2
order by sum(hours_viewed) desc
limit 20;

--tv series
select
	season_id,
	tv_show_id,
	title,
	sum(hours_viewed) total_jam,
	sum(views) total_penonton
from view_summary vs
left join season s 
	on vs.season_id = s.id
where season_id is not NULL
group by 1,2,3
order by 4 desc
limit 20;


--Bagaimana tren penayangan berubah seiring waktu?
select
	movie_id,
	m.title,
	DATE(date_trunc('Month', start_date)) date_month,
	sum(hours_viewed) jam_tonton,
	SUM(views) jumlah_penonton
from view_summary vs
left join movie m
	on vs.movie_id = m.id
where movie_id is not null
group by 1,2,3
order by 3 asc;

select
	DATE(date_trunc('Month', start_date)) date_month,
	sum(hours_viewed) jam_tonton,
	SUM(views) jumlah_penonton
from view_summary vs
where movie_id is not null
group by 1
order by 1;

select
	DATE(date_trunc('Month', start_date)) date_month,
	sum(hours_viewed) jam_tonton,
	SUM(views) jumlah_penonton,
	SUM(hours_viewed)/COUNT(distinct movie_id) jam_tonton_per_movie,
	COUNT(distinct movie_id) jumlah_movie
from view_summary vs
where movie_id is not null
group by 1
order by 1;


--Apakah ada hubungan antara durasi tayang dan tingkat popularitas sebuah konten?
select 
	movie_id,
	m.title,
	duration,
	hours_viewed
from view_summary vs
left join movie m
	on vs.movie_id = m.id
where movie_id is not null;
--
SELECT
  m.title,
  m.runtime,
  SUM(vs.hours_viewed) AS total_hours_viewed,
  SUM(vs.views) AS total_views,
  AVG(vs.view_rank) AS avg_rank,
  SUM(vs.cumulative_weeks_in_top10) AS total_weeks_top10
FROM
  movie m
JOIN
  view_summary vs ON m.id = vs.movie_id
GROUP BY
  m.id, m.title, m.runtime
order by
	3 desc;
--
SELECT
  CASE
    WHEN m.runtime < 90 THEN 'Short'
    WHEN m.runtime >= 90 AND m.runtime <= 120 THEN 'Medium'
    ELSE 'Long'
  END AS duration_category,
  COUNT(m.id) AS total_titles,
  AVG(vs.hours_viewed) AS avg_hours_viewed,
  AVG(vs.views) AS avg_views
FROM
  movie m
JOIN
  view_summary vs ON m.id = vs.movie_id
GROUP BY
  duration_category;
--
select 
    case 
	    when runtime >= 120 then '>=120 minutes'
	    when runtime >= 100 then '>=100 minutes'
	    when runtime >= 80 then '>=80 minutes'
	    when runtime >= 50 then '>=50 minutes'
	    else '<50 minutes'
    end as runtime_group,
    SUM(hours_viewed) total_view_hour,
    AVG(hours_viewed) average_view_hour,
    AVG("views") average_views,
    count(distinct movie_id) num_movies
from movie m
left join view_summary vs
	on m.id = vs.movie_id
where m.runtime is not null
group by 1;

	

--Apakah Acara TV dengan lebih banyak musim memiliki penayangan lebih tinggi?
SELECT
  tv.title,
  COUNT(s.id) AS season_count,
  SUM(vs.views) AS total_views,
  AVG(vs.views) AS avg_views_per_summary
FROM
  tv_show tv
JOIN
  season s ON tv.id = s.tv_show_id
JOIN
  view_summary vs ON s.id = vs.season_id
GROUP BY
  tv.id, tv.title
ORDER BY
  total_views DESC;
----
with raw as (
	select 
		tv_show_id, 
		ts.title,
		count(distinct s.id) num_season,
		SUM(hours_viewed) total_jam_tonton,
		SUM("views") total_views
	from season s
	left join view_summary vs
		on s.id = vs.season_id
	left join tv_show ts
		on ts.id = s.tv_show_id
	group by 1,2
	order by 3 desc
	)
select
	num_season,
	avg(total_jam_tonton) avg_jam_tonton,
	avg("total_views") avg_views
from raw
group by 1;

--Apakah ada pola menarik dalam kebiasaan menonton penonton dari sisi waktu tonton per tayangan?
with summary as (
	select
		DATE(date_trunc('Month', start_date)) date_month,
		avg(views) avg_view,
		avg(hours_viewed) avg_hours_viewed
	from view_summary vs
	group by 1
	)
select 
	extract(month from date_month) month_,
	avg(avg_view) avg_view,
	avg(avg_hours_viewed) avg_hour_viewed
from summary
group by 1;
--hari libur

--Konten apa saja yang menunjukkan performa terbaik dalam enam bulan terakhir?
--movie
select 
	movie_id,
	title,
	sum(views) total_penonton,
	sum(hours_viewed) total_jam_ditonton 
from view_summary vs
left join movie m
	on vs.movie_id = m.id
where movie_id is not null
	and start_date >= CURRENT_DATE - interval '6 MONTHS'
group by 1,2
order by 3 DESC;

--tv show
select 
	season_id,
	title,
	sum(views) total_penonton,
	sum(hours_viewed) total_jam_ditonton 
from view_summary vs
left join season m
	on vs.season_id = m.id
where season_id is not null
	and start_date >= CURRENT_DATE - interval '6 MONTHS'
group by 1,2
order by 3 DESC;
