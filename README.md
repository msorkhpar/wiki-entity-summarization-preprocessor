![GitHub License](https://img.shields.io/github/license/msorkhpar/wiki-entity-summarization-preprocessor)

# Wiki Entity Summarization Pre-processing

## Overview

This project focuses on the pre-processing steps required for the Wiki Entity Summarization (Wiki ES) project. It
involves building the necessary databases and loading data from various sources to prepare for the entity summarization
tasks.

### Server Specifications

For the pre-processing steps, we used an r5a.4xlarge instance on AWS with the following specifications:

- vCpu: 16 (AMD EPYC 7571, 16 MiB cache, 2.5 GHz)
- Memory: 128 GB (DDR4, 2667 MT/s)
- Storage: 500 GB (EBS, 2880 Max Bandwidth)

### Getting Started

To get started with the pre-processing, follow these steps:

1. Build the [wikimapper](https://github.com/jcklie/wikimapper) database:

```shell
pip install wikimapper
````

If you would like to download the latest version, run the following:

```shell
EN_WIKI_REDIRECT_AND_PAGES_PATH={your_files_path}
wikimapper download enwiki-latest --dir $EN_WIKI_REDIRECT_AND_PAGES_PATH
```

After having `enwiki-{VERSION}-page.sql.gz`, `enwiki-{VERSION}-redirect.sql.gz`,
and `enwiki-{VERSION}-page_props.sql.gz` loaded under your data directory, run the following commands:

```shell
VERSION={VERSION}
EN_WIKI_REDIRECT_AND_PAGES_PATH={your_files_path}
INDEX_DB_PATH="`pwd`/data/index_enwiki-$VERSION.db"
wikimapper create enwiki-$VERSION --dumpdir $EN_WIKI_REDIRECT_AND_PAGES_PATH --target $INDEX_DB_PATH
```

2. Load the created database into the Postgres database:
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

3. Correct missing data: After running the experiments, some issues were encountered with the wikimapper library.
   To correct the missing data, run the following script:

```shell 
python3 missing_data_correction.py
```

## Data Sources

The pre-processing steps involve loading data from the following sources:

- **Wikidata**, [wikidatawiki latest version](https://dumps.wikimedia.org/wikidatawiki/latest/):
  First, download the latest version of the Wikidata dump. With the dump, you can run the following command to load the
  metadata of the Wikidata dataset into the Postgres database, and the relationships between the entities into the Neo4j
  database. This module is called `Wikidata Graph Builder (wdgp)`.
  ```shell
  docker-compose up wdgp
  ```
- **Wikipedia**, [enwiki lastest version](https://dumps.wikimedia.org/enwiki/latest/):
  The Wikipedia pages are used to extract the abstract and infobox of the corresponding Wikidata entity. The abstract
  and infobox are then used to annotate the summary in Wikidata. To provide such information, you need to load the
  latest version of the Wikipedia dump into the Postgres database. This module is called `Wikipedia Page Extractor (
  wppe)`.
    ```shell
    docker-compose up wppe
    ```

## Summary Annotation

When both datasets are loaded into the databases, we start processing all the available pages in the Wikipedia dataset
to extract the abstract and infobox of the corresponding Wikidata entity. Later, these pages are marked from the
extracted data, and the edges containing the marked pages are marked as candidates. Since Wikidata is a heterogeneous
graph with multiple types of edges, we need to pick the most relevant edge as a summary between two entities for the
summarization task. This module is called `Wiki Summary Annotator (wsa)`, and we
use [DistilBERT](https://arxiv.org/abs/1910.01108)  to filter the most relevant edge.

```shell
docker-compose up wsa
```

## Conclusion

By running the above commands, you will have the necessary databases and data loaded to start the Wiki Entity
Summarization project. The next steps involve providing a set of seed nodes based on your preference along with other
configuration parameters to get a fully customized Entity Summarization Dataset.

## License

This project is licensed under the CC BY 4.0 License. See the [LICENSE](LICENSE) file for details.
