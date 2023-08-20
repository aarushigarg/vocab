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
    create_time timestamp default now()
);

create unique index if not exists saved_words_idx on saved_words (user_id, word);

create table if not exists cached_words (
    word varchar(512) primary key,
    data jsonb not null,
    create_time timestamp default now(),
    update_time timestamp default now()
);

create type pos as enum ('noun', 'pronoun', 'verb', 'adjective', 'adverb', 'preposition', 'conjunction', 'interjection', 'phrase');
create table if not exists word_defns (
    id serial primary key,
    word varchar(512) not null,
    part_of_speech pos not null,
    defn varchar(8192) not null,
    examples varchar(8192)[],
    user_id int,
    create_time timestamp default now(),
    update_time timestamp default now()
);

create table if not exists word_defn_lists (
    id serial primary key,
    user_id int not null,
    name varchar(512) not null,
    create_time timestamp default now(),
    update_time timestamp default now()
);

create table if not exists word_defn_list_map (
    word_defn_list_id int not null,
    word_defn_id int not null,
    create_time timestamp default now(),
    primary key(word_defn_list_id, word_defn_id)
);

create table if not exists practice_sessions (
    id serial primary key,
    user_id int not null,
    wdl_id int not null,
    word_defn_ids int [] not null,
    current_index int default 0,
    create_time timestamp default now(),
    update_time timestamp default now()
);

create type recall_difficulty_level as enum ('easy', 'difficult', 'couldnt_recall');
create table if not exists feedback (
    id serial primary key,
    user_id int not null,
    word_defn_id int not null,
    difficulty_level recall_difficulty_level not null,
    create_time timestamp default now(),
    update_time timestamp default now()
);