from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from functools import wraps
from typing import List

from more_itertools import batched

import psycopg2
from psycopg2 import pool
from neo4j import GraphDatabase, Driver, Session
from dotenv import load_dotenv
import datetime as dt
import atexit

load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, ".env"))
POSTGRES_HOST = os.getenv("DB_HOST")
POSTGRES_DB = os.getenv("DB_NAME")
POSTGRES_USER = os.getenv("DB_USER")
POSTGRES_PASS = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
MAX_CONNECTION_POOL = os.getenv("MAX_DB_CONNECTION_POOL")

NEO4J_URI = f"bolt://{os.getenv('NEO4J_HOST')}:7687"
NEO4J_DB = "neo4j"
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_AUTH = (
    NEO4J_USER,
    NEO4J_PASSWORD,
)

postgresql_pool = psycopg2.pool.ThreadedConnectionPool(
    1, MAX_CONNECTION_POOL,
    user=POSTGRES_USER, password=POSTGRES_PASS,
    host=POSTGRES_HOST, port=DB_PORT,
    database=POSTGRES_DB
)


def close_postgresql_pool():
    if postgresql_pool:
        postgresql_pool.closeall()
        print("PostgreSQL connection pool has been closed.")


atexit.register(close_postgresql_pool)

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=NEO4J_AUTH,
    max_connection_lifetime=30 * 60,  # 30 minutes
    max_connection_pool_size=50,  # Maximum number of connections in the pool
    connection_acquisition_timeout=5 * 60  # 2 minutes
)
atexit.register(driver.close)


def bulk_fetch_wikipedia_titles(wikipedia_titles: list[str]) -> dict[str, tuple[str, str, str]]:
    connection = None
    records = {}
    query = """SELECT wp.id, wp.title, m.wikidata_id
                               FROM wiki_page_to_wiki_data_mappings m
                               RIGHT JOIN wikipedia_pages wp ON m.wikipedia_id = wp.id  WHERE wp.title in %s;"""
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (tuple(wikipedia_titles),))
                results = cursor.fetchall()
                for result in results:
                    records[result[1]] = (result[0], result[1], result[2])
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while fetching abstract", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)
    return records


def fetch_wiki_mapping(identifier: str) -> tuple[str, str, str] | None:
    '''
    Fetch the wikipedia_id, wikipedia_title, and wikidata_id from the database
    :param identifier:
    :return:  (wikipedia_id, wikipedia_title, wikidata_id)
    '''
    connection = None
    record = None
    query = """SELECT wp.id, wp.title, m.wikidata_id
                               FROM wiki_page_to_wiki_data_mappings m
                               RIGHT JOIN wikipedia_pages wp ON m.wikipedia_id = wp.id 
                               """
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                if type(identifier) is int:
                    query += " WHERE m.wikipedia_id = %s;"
                elif identifier.isdigit():
                    query += " WHERE m.wikipedia_id = %s;"
                elif re.match(r'^Q\d+$', identifier) is not None:
                    query += " WHERE m.wikidata_id = %s;"
                else:
                    query += " WHERE m.wikipedia_title = %s;"
                cursor.execute(query, (identifier,))
                result = cursor.fetchone()
                if result:
                    record = (result[0], result[1], result[2])
                elif type(identifier) is str and identifier.startswith("Q"):
                    record = (None, None, identifier)
                else:
                    record = (None, None, None)
                    print(query)
                    print("Identifier not found!!!", identifier)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while fetching abstract", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)
    return record


@lru_cache(maxsize=1024)
def fetch_predicate_metadata(predicate_id: str) -> tuple(str, str) | None:
    connection = None
    record = None
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT property_label ,description from predicates where property_id = %s",
                               (predicate_id,))
                result = cursor.fetchone()
                if result:
                    record = result[0], result[1]
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while fetching predicate metadata", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)
    return record


@lru_cache(maxsize=1024)
def fetch_wikidata_metadata(wikidata_id) -> tuple[str, str] | None:
    '''
    Fetch the label and description of the wikidata_id
    :param wikidata_id:
    :return: (label,  description)
    '''
    connection = None
    record = None
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT label, description from subjects where name = %s", (wikidata_id,))
                result = cursor.fetchone()
                if result:
                    record = (result[0], result[1])
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while fetching wikidata metadata", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)
    return record


def fetch_wikipedia_page_content(wikipedia_title) -> str:
    connection = None
    record = None
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT content from wikipedia_pages where title = %s", (wikipedia_title,))
                result = cursor.fetchone()
                if result:
                    record = result[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while fetching page content", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)
    return record


def fetch_unprocessed_wikipedia_pages() -> list[tuple[str, str, str]] | None:
    """
    Fetch unprocessed wikipedia pages
    :return: [(wikipedia_id, wikipedia_title, wikidata_id)]
    """
    connection = None
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM wikipedia_pages
                    WHERE processed = FALSE
                    order by id
                    LIMIT 500 FOR UPDATE SKIP LOCKED;
                    """)
                return cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while fetching unprocessed pages", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)
    return None


def mark_wikipedia_page_processed(root_wikipedia_id):
    connection = None
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE wikipedia_pages SET processed = TRUE WHERE id = %s",
                               (root_wikipedia_id,))
                connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while updating processed field", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)


def mark_wikipedia_page_process_failed(root_wikipedia_id):
    connection = None
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE wikipedia_pages SET processed = null WHERE id = %s",
                               (root_wikipedia_id,))
                connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while updating processed field", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)


def insert_missing_mappings(wikipedia_id, wikipedia_title, wikidata_id):
    connection = None
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                if wikidata_id:
                    cursor.execute(
                        "INSERT INTO wiki_page_to_wiki_data_mappings(wikipedia_id, wikipedia_title, wikidata_id)"
                        " VALUES (%s, %s, %s)",
                        (wikipedia_id, wikipedia_title, wikidata_id))
                if not wikidata_id:
                    cursor.execute("UPDATE wikipedia_pages SET processed = TRUE WHERE id = %s",
                                   (wikipedia_id,))
                connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while updating processed field", error)
    finally:
        if connection:
            postgresql_pool.putconn(connection)


def create_neo4j_session() -> tuple[Driver, Session]:
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    return driver, driver.session(database=NEO4J_DB)


def close_neo4j_session(driver, session):
    if session:
        session.close()
    if driver:
        driver.close()


from threading import local

# Thread-local storage for session management
thread_local = local()


def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = driver.session(database=NEO4J_DB)
    return thread_local.session


def close_session():
    if hasattr(thread_local, 'session'):
        thread_local.session.close()
        del thread_local.session


def manage_neo4j_session(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        session = get_session()
        try:
            result = f(*args, session=session, **kwargs)
            return result
        finally:
            close_session()

    return wrapped


# TODO create indexes if not exists
# CREATE INDEX summary_summary_for_index FOR ()-[r:SUMMARY]->() ON (r.summary_for);
# CREATE INDEX wiki_entity_entityName_index FOR (n:WikiEntity) ON (n.entityName);

@lru_cache(maxsize=1024)
@manage_neo4j_session
def fetch_relations(subject_qid: str, object_qid: str, session) -> list[tuple[str, str, str]]:
    candidates = set()
    query = """
            MATCH (
                s:WikiEntity {entityName: $subject_qid})-[r:HAS_TYPE]->(t:WikiEntity {entityName: $target_qid}
            )
            RETURN s.entityName as s, r.type as p, t.entityName as t
    """

    result = session.run(query, subject_qid=object_qid, target_qid=subject_qid)
    for record in result:
        candidates.add(record)
    result = session.run(query, subject_qid=subject_qid, target_qid=object_qid)
    for record in result:
        candidates.add(record)

    return list(map(lambda x: (x['s'], x['p'], x['t']), candidates))


@manage_neo4j_session
def fetch_edges_by_candidates(edge_candidates: list[tuple[str, str]], session) -> list[tuple[str, str, str]]:
    query = """UNWIND $candidates AS candidate
    MATCH (s:WikiEntity {entityName: candidate[0]})-[r:HAS_TYPE]->(t:WikiEntity {entityName: candidate[1]})
    RETURN s.entityName as s, r.type as p, t.entityName as t"""
    result = []
    records = session.run(query, candidates=edge_candidates)
    for record in records:
        result.append((record['s'], record['p'], record['t']))
    return result


@manage_neo4j_session
def fetch_first_neighbors(wikidata_id: str, session):
    query = """
    MATCH (s:WikiEntity {entityName: $wikidata_id})-[r:HAS_TYPE]-(t:WikiEntity)
    RETURN STARTNODE(r).entityName AS s, r.type as p, ENDNODE(r).entityName as t
    """
    result = []
    records = session.run(query, wikidata_id=wikidata_id)
    for record in records:
        result.append((record['s'], record['p'], record['t']))
    return result


@manage_neo4j_session
def fetch_in_edges(wikidata_id: str, session) -> list[tuple[str, str, str]]:
    query = """
        MATCH (s:WikiEntity {entityName: $wikidata_id})-[r:HAS_TYPE]->(t:WikiEntity)
        RETURN s.entityName AS s, r.type as p,t.entityName as t
        """
    result = []
    records = session.run(query, wikidata_id=wikidata_id)
    for record in records:
        result.append((record['s'], record['p'], record['t']))
    return result


@manage_neo4j_session
def fetch_out_edges(wikidata_id: str, session) -> list[tuple[str, str, str]]:
    query = """
            MATCH (s:WikiEntity)-[r:HAS_TYPE]->(t:WikiEntity {entityName: $wikidata_id})
            RETURN s.entityName AS s, r.type as p,t.entityName as t
            """
    result = []
    records = session.run(query, wikidata_id=wikidata_id)
    for record in records:
        result.append((record['s'], record['p'], record['t']))
    return result


@manage_neo4j_session
def fetch_summaries(wikidata_id, session) -> list[tuple[str, str, str]] | None:
    # fetch the summary edges that has wikidata_id marked as summary_for
    query = """
        MATCH (s:WikiEntity)-[r:SUMMARY {summary_for: $wikidata_id}]->(t:WikiEntity)
        WHERE s.entityName = $wikidata_id OR t.entityName = $wikidata_id
        RETURN s.entityName AS s, r.predicate as p, t.entityName as t
    """
    result = []
    records = session.run(query, wikidata_id=wikidata_id)
    for record in records:
        result.append((record['s'], record['p'], record['t']))
    return result


@manage_neo4j_session
def add_summary_edge(root_wikidata_id, from_entity, predicate, to_entity, session) -> tuple[str, str, str] | None:
    # fetch the edge and append summary_for with root_wikidata_id as an attribute
    query = """
      MATCH (s:WikiEntity {entityName: $from_entity}), (t:WikiEntity {entityName: $to_entity})
        MERGE (s)-[r:SUMMARY {summary_for: $root_wikidata_id, predicate: $predicate}]->(t)
        RETURN s, r, t
    """
    result = session.run(query, from_entity=from_entity, to_entity=to_entity, root_wikidata_id=root_wikidata_id,
                         predicate=predicate)
    return result.single()


@manage_neo4j_session
def label_candidates(candidates, session) -> list[str]:
    label_base_name = f"Candidates_{dt.datetime.now().timestamp()}_"
    component_labels = []
    for i, candidate in enumerate(candidates):
        candidate_label = f"{label_base_name}{i + 1}"
        component_labels.append(candidate_label)
        for batch_nodes in batched(candidate, 1000):
            session.run(
                f"""
                UNWIND $node_names AS node_name
                MATCH (n:WikiEntity {{entityName: node_name}})
                SET n:{candidate_label}""",
                node_names=batch_nodes
            )
        session.run(f"CREATE INDEX FOR (n:{candidate_label}) ON (n.entityName)")
    return component_labels


@manage_neo4j_session
def change_component_label_with(from_label, to_label, session):
    session.run(f"""
    MATCH(m:$from_label)
    SET m:$to_label
    REMOVE m:$from_label
    """, from_label=from_label, to_label=to_label)
    session.run(f"DROP INDEX FOR (n:{from_label}) ON (n.entityName)")


@manage_neo4j_session
def remove_component_labels(component_labels, session):
    for component_label in component_labels:
        session.run(f"""
        MATCH(m:$component_label)
        REMOVE m:$component_label
        """, component_label=component_label)
        session.run(f"DROP INDEX FOR (n:{component_label}) ON (n.entityName)")


@manage_neo4j_session
def fetch_shortest_pairs_between_components_cypher(component_label_a, component_label_b, max_depth=1, k=10,
                                                   session=None) -> list[tuple[str, str]]:
    k = min(k, min(len(component_label_a), len(component_label_b)))
    top_pairs = []
    results = session.run(
        f"""
            (a:$component_label_a), (b:$componentBLabel), path = shortestPath((a)-[*..$maxDepth]-(b))
            WHERE a <> b
            RETURN a.entityName AS a, b.entityName AS b, length(path) AS hops
            ORDER BY hops ASC
            LIMIT $k
        """, componentALabel=component_label_a, componentBLabel=component_label_b, k=k, maxDepth=max_depth
    )
    for record in results:
        if record['path']:
            top_pairs.append((record['a'], record['b']))
    return top_pairs


@manage_neo4j_session
def fetch_shortest_path(a, b, session) -> list[tuple[str, str, str]]:
    record = session.run("""
    MATCH (a:WikiEntity {entityName: $a}), (b:WikiEntity {entityName: $b}) , path = shortestPath((a)-[*]-(b))
    WHERE a <> b
    RETURN [i IN RANGE(0, LENGTH(path)-1) | 
        {
            start_node: STARTNODE(RELATIONSHIPS(path)[i]).entityName, 
            predicate: RELATIONSHIPS(path)[i].type,
            end_node: ENDNODE(RELATIONSHIPS(path)[i]).entityName
        }
    ] AS legs
    """, a=a, b=b)
    path = list()
    for leg in record.single()["legs"]:
        path.append((leg['start_node'], leg['predicate'], leg['end_node']))
    return path


@manage_neo4j_session
def fetch_shortest_paths(pairs: list[tuple[str, str]], session) -> list[list[tuple[str, str, str]]]:
    query = """
    UNWIND $pairs AS pair
    MATCH (a:WikiEntity {entityName: pair.a}), (b:WikiEntity {entityName: pair.b}) , path = shortestPath((a)-[*]-(b))
    WHERE a <> b
    RETURN collect([
        i IN RANGE(0, LENGTH(path)-1) | 
        (
            start_node: STARTNODE(RELATIONSHIPS(path)[i]).entityName, 
            predicate: RELATIONSHIPS(path)[i].type,
            end_node: ENDNODE(RELATIONSHIPS(path)[i]).entityName
        )
    ]) AS legs
    """
    records = session.run(query, pairs=[{'a': a, 'b': b} for a, b in pairs])
    results = []
    for record in records:
        path = list()
        for leg in record["legs"]:
            path.append((leg['start_node'], leg['predicate'], leg['end_node']))
        results.append(path)

    return results
