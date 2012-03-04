drop table events cascade;
create table events (
id serial unique,
hash varchar(21) unique,
source varchar(128),
lat float not null,
lon float not null,
time timestamp not null,
addtime timestamp default current_timestamp,
title varchar(256) not null,   
shorttxt varchar(1024),
fulltxt text
);
create index e_latlon on events(lat, lon);
create index e_time on events(time);
create index e_id on events(id);

drop  table imgs cascade;
create table imgs (
id serial,
eid int references events(id), 
url varchar(1024),
blob bytea
);
create index imgs_eid on imgs(eid);


drop table metadata cascade;
create table metadata (
id serial,
eid int references events(id),
key varchar(1024),
val varchar(1024)
);
create index m_id on metadata(id);

drop table scrapers;
create table scrapers (
id serial,
lat float,
lon float,
radius float
);

drop table pendingqs;
create table pendingqs (
id serial,
lat float,
lon float,
radius float
);