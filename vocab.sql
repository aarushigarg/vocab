create database vocabdb;
create user vocabuser with password 'vocabpass';
grant connect on database vocabdb to vocabuser;
grant usage on schema public to vocabuser;
grant all privileges on all tables in schema public to vocabuser;
grant all privileges on all sequences in schema public to vocabuser;

\c vocabdb

create table if not exists users (
    id serial primary key,
    username varchar (32) unique not null,
    email varchar (512) unique not null,
    avatar varchar (2048) not null,
    is_active boolean default true,
    is_admin boolean default false,
    create_time timestamp default now(),
    update_time timestamp default now()
);