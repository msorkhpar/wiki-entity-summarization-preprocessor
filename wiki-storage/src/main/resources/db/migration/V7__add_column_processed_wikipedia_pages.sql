alter table wikipedia_pages
    add if not exists processed boolean default false;

