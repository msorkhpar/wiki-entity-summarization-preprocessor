create table wikipedia_pages
(
    id                BIGINT primary key,
    title             VARCHAR(255),
    content           TEXT,
    content_length    INTEGER
);

create index idx_wikipedia_pages_title
    on wikipedia_pages (title);