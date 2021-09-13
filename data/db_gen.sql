create table character
(
    char_id     integer
        primary key,
    server      text    not null,
    race        text    not null,
    lvl         integer not null,
    char_class  text    not null,
    description text    not null,
    heavens     text    not null,
    doll        text    not null
);

create table message_history
(
    message_id int
        constraint message_history_pk
            primary key,
    chat_id    int not null,
    is_pinned  boolean default false not null
);

create table user
(
    user_id   integer
        primary key,
    username  text not null,
    full_name text not null
);

create table lot
(
    lot_id      integer
        primary key,
    char_id     integer   not null
        references character,
    user_id     integer   not null
        references user,
    date_opened timestamp not null,
    date_close  timestamp,
    price       float     not null,
    contact     text      not null
);

create table session
(
    session_id    integer
        primary key,
    user_id       integer   not null
        references user,
    session_start timestamp not null
);

create table new_lot_session
(
    session_id   integer
        primary key
        references session,
    server       text,
    race         text,
    lvl          integer,
    char_class   text,
    description  text,
    heavens      text,
    doll         text,
    price        float,
    contact_info text
);

create table search_session
(
    session_id integer
        primary key
        references session,
    server     text,
    race       text
);

create table user_event
(
    name text
        constraint user_event_pk
            primary key
);

create table user_actions
(
    act_id     int
        constraint user_actions_pk
            primary key,
    user_id    int       not null
        references user,
    event_time timestamp not null,
    event      text      not null
        references user_event
);

