create table character
(
    char_id         integer primary key,
    server          text not null,
    race            text not null,
    lvl             integer not null,
    class           text not null,
    description     text not null,
    heavens         text not null,
    doll            text not null
);

create table user
(
    user_id         integer primary key
);

create table lot
(
    lot_id          integer primary key,
    char_id         integer not null
                        references character,
    user_id         integer not null
                        references user,
    date_opened     timestamp not null,
    date_close      timestamp,
    price           float not null,
    contact         text not null
);