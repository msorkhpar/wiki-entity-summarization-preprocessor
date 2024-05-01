#! /usr/bin/env bash

volumes() {
  echo "
########## Volumes ##########
POSTGRES_VOLUME_PATH=/data/pg-data
NEO4J_VOLUME_PATH=/data/neo4j-data
WIKIDATA_DUMPS_PATH=/data/wikidata/articles/
WIKIPEDIA_DUMPS_PATH=/data/wikipedia/articlesdump/
JUPYTER_VOLUME_PATH=/data/jupyter-data
OUTPUT_VOLUME_PATH=/data/wiki-es-output
"
}

auths() {
  echo "
########## Auth ##########
DB_NAME=wikies
DB_USER=wikies
DB_PASSWORD=password
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
JUPYTER_TOKEN=wikies
"
}

hosts() {
  echo "
########## Hosts ##########
DB_HOST=wiki-es-pg
NEO4J_HOST=wiki-es-neo
"
}

ports() {
  echo "
########## Ports ##########
DB_PORT=5432
"
}

pg_env() {
  echo "# Postgres
########################################################################
POSTGRES_DB=\${DB_NAME}
POSTGRES_USER=\${DB_USER}
POSTGRES_PASSWORD=\${DB_PASSWORD}
"
}

neo4j_env() {
  echo "# Neo4j
########################################################################
NEO4J_AUTH=\${NEO4J_USER}/\${NEO4J_PASSWORD}
NEO4J_PLUGINS='[\"graph-data-science\",\"apoc\"]'
NEO4J_dbms_security_procedures_unrestricted=gds.*
NEO4J_server_config_strict__validation_enabled=false
########## Memory configurations ##########
NEO4J_server_memory_heap_initial__size=1000m
NEO4J_server_memory_heap_max__size=1000m
NEO4J_server_memory_pagecache_size=1000m
NEO4J_dbms_memory_transaction_total_max=1000m
"
}


wdgb_env() {
  echo "# Wikidata Graph Builder
########################################################################
APP_DUMPFILES_DIR=\${WIKIDATA_DUMPS_PATH}
APP_MODE=MIGRATION # MIGRATION or EXTRACTION
APP_DUMPFILES_pattern=*pages-articles*xml*.bz2
APP_DUMPFILES_MULTISTREAM=True
APP_EXECUTORPOOL_COREPOOLSIZE=20
SPRING_DATASOURCE_URL=jdbc:postgresql://wiki-es-pg:\${DB_PORT}/\${DB_NAME}
SPRING_DATASOURCE_USERNAME=\${DB_USER}
SPRING_DATASOURCE_PASSWORD=\${DB_PASSWORD}
SPRING_NEO4J_AUTHENTICATION_USERNAME=\${NEO4J_USER}
SPRING_NEO4J_AUTHENTICATION_PASSWORD=\${NEO4J_PASSWORD}
SPRING_NEO4J_URI=bolt://wiki-es-neo:7687
"
}

wppe_env() {
  echo "# Wikipedia Page Extractor
########################################################################
APP_DUMPFILES_DIR=\${WIKIPEDIA_DUMPS_PATH}
APP_DUMPFILES_pattern=*pages-articles*xml*.bz2
APP_EXECUTORPOOL_COREPOOLSIZE=10
SPRING_DATASOURCE_URL=jdbc:postgresql://wiki-es-pg:\${DB_PORT}/\${DB_NAME}
SPRING_DATASOURCE_USERNAME=\${DB_USER}
SPRING_DATASOURCE_PASSWORD=\${DB_PASSWORD}
"
}

initialize_env() {
  echo "*************************************"
  local env_file=$1
  local template_function=$2
  if [ ! -f "$env_file" ]; then
    echo "Creating $env_file..."
    mkdir -p "$(dirname "$env_file")"
    touch "$env_file"
  fi
  echo "[appending '$template_function()' to '$env_file']"
  while IFS= read -r line; do
    if ! grep -q "^${line%%=*}" "$env_file"; then
      echo "$line" >>"$env_file"
    fi
  done < <($template_function)
}

echo "Creating config files..."

initialize_env ".env" volumes
initialize_env ".env" auths
initialize_env ".env" ports
initialize_env ".env" hosts
initialize_env "./configs/pg.env" pg_env
initialize_env "./configs/neo4j.env" neo4j_env
initialize_env "./configs/wdgb.env" wdgb_env
initialize_env "./configs/wppe.env" wpte_env

echo "*************************************"
echo "Done."
