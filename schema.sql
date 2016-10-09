drop table if exists entries;
PRAGMA foreign_keys = ON;
create table entries (
	id integer primary key autoincrement,
	title text not null,
	time DATETIME DEFAULT CURRENT_TIMESTAMP,
	'text' text not null,	
	likes integer default 0
);

drop table if exists commentonentries;
create table commentonentries (
	id integer primary key autoincrement,
	comment_id integer,
	commenttext text not null,
	foreign key(comment_id) references entries(id)
);