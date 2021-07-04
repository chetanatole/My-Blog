create table user( 
    id integer primary key autoincrement,
    username varchar(120) not null unique,
    email varchar(255) not null unique,
    passwordval varchar(255) not null,
    image_file varchar(255) not null default 'default.jpg'
);
create table post(
    id integer primary key autoincrement,
    title varchar(255) not null,
    intro varchar(1000) not null,
    image_file varchar(255), 
    date_posted datetime default current_timestamp,
    content varchar(1000) not null,
    user_id integer ,
    foreign key(user_id) references user(id)
);