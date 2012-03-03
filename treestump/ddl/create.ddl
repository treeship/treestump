drop table events cascade;
create table events (
id serial unique,
hash varchar(21) unique,
lat float not null,
lon float not null,
time timestamp not null,
addtime timestamp default current_timestamp,
title varchar(256),  
shorttxt varchar(1024),
fulltxt text
);

drop  table imgs cascade;
create table imgs (
id serial,
eid int references events(id), 
url varchar(1024),
blob bytea
);
