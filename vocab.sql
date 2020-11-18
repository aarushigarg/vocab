create database vocabdb;
create user vocabuser with password 'vocabpass';
grant connect on database vocabdb to vocabuser;
grant usage on schema public to vocabuser;
grant all privileges on all tables in schema public to vocabuser;
grant all privileges on all sequences in schema public to vocabuser;

\c vocabdb

create table if not exists users (
    id serial primary key,
    username varchar(32) unique not null,
    email varchar(512) unique not null,
    avatar varchar(2048) not null,
    is_active boolean default true,
    is_admin boolean default false,
    create_time timestamp default now(),
    update_time timestamp default now()
);

create table if not exists saved_words (
    id serial primary key,
    user_id int not null,
    word varchar(256) not null,
    word_defn_id varchar(16) not null,
    create_time timestamp default now()
);

create unique index saved_words_idx on saved_words (user_id, word, word_defn_id);

create table if not exists cached_words (
    word varchar(512) primary key,
    data jsonb not null,
    create_time timestamp default now(),
    update_time timestamp default now()
);