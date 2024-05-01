# Wiki ES

## Overview

## Getting Started

- Build [wikimapper](https://github.com/jcklie/wikimapper) database

```shell
pip install wikimapper
````

If you would like to download the latest version run the following

```shell
EN_WIKI_REDIRECT_AND_PAGES_PATH={your_files_path}
wikimapper download enwiki-latest --dir $EN_WIKI_REDIRECT_AND_PAGES_PATH
```   

After having `enwiki-{VERSION}-page.sql.gz`, `enwiki-{VERSION}-redirect.sql.gz`,
and `enwiki-{VERSION}-page_props.sql.gz` loaded under your data directory:

```shell
VERSION={VERSION}
EN_WIKI_REDIRECT_AND_PAGES_PATH={your_files_path}
INDEX_DB_PATH="`pwd`/data/index_enwiki-$VERSION.db"
wikimapper create enwiki-$VERSION --dumpdir $EN_WIKI_REDIRECT_AND_PAGES_PATH --target $INDEX_DB_PATH
```

- Now load the created db into our Postgres database,
  read [pgloader's document](https://pgloader.readthedocs.io/en/latest/install.html) for the installation

```shell
./config-files-generator.sh
source .env
cat <<EOT > sqlite-to-page-migration.load
load database
    from $INDEX_DB_PATH
    into postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME
with include drop, create tables, create indexes, reset sequences
;
EOT

pgloader ./sqlite-to-page-migration.load
```