from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

import psycopg2
from psycopg2 import pool
from neo4j import GraphDatabase, Driver, Session
from dotenv import load_dotenv

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

postgresql_pool = psycopg2.pool.SimpleConnectionPool(
    1, MAX_CONNECTION_POOL,
    user=POSTGRES_USER, password=POSTGRES_PASS,
    host=POSTGRES_HOST, port=DB_PORT,
    database=POSTGRES_DB
)


def create_session() -> tuple[Driver, Session]:
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    return driver, driver.session(database=NEO4J_DB)


def close_session(driver, session):
    if session:
        session.close()
    if driver:
        driver.close()


def bulk_fetch_wikipedia_titles(wikipedia_titles: list[str]) -> dict[str, tuple[str, str, str]]:
    connection = None
    records = {}
    query = """SELECT m.wikipedia_id, m.wikipedia_title, m.wikidata_id
                               FROM wiki_page_to_wiki_data_mappings m
                               RIGHT JOIN wikipedia_pages wp ON m.wikipedia_title = wp.title WHERE m.wikipedia_title in %s;"""
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
    query = """SELECT m.wikipedia_id, m.wikipedia_title, m.wikidata_id
                               FROM wiki_page_to_wiki_data_mappings m
                               RIGHT JOIN wikipedia_pages wp ON m.wikipedia_title = wp.title """
    try:
        connection = postgresql_pool.getconn()
        if connection:
            with connection.cursor() as cursor:
                if type(identifier) == int or identifier.isdigit():
                    query += " WHERE m.wikipedia_id = %s;"
                elif re.match(r'^Q\d+$', identifier) is not None:
                    query += " WHERE m.wikidata_id = %s;"
                else:
                    query += " WHERE m.wikipedia_title = %s;"
                cursor.execute(query, (identifier,))
                result = cursor.fetchone()
                if result:
                    record = (result[0], result[1], result[2])
                elif identifier.startswith("Q"):
                    record = (None, None, identifier)
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
                    LIMIT 200 FOR UPDATE SKIP LOCKED;
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


@lru_cache(maxsize=1024)
def fetch_relations(subject_qid: str, object_qid: str, session=None) -> list[tuple[str, str, str]]:
    candidates = set()
    query = """
            MATCH (
                s:WikiEntity {entityName: $subject_qid})-[r:HAS_TYPE]->(t:WikiEntity {entityName: $target_qid}
            )
            RETURN s.entityName as s, r.type as p, t.entityName as t
    """

    def exec_query(session, candidates):
        result = session.run(query, subject_qid=object_qid, target_qid=subject_qid)
        for record in result:
            candidates.add(record)
        result = session.run(query, subject_qid=subject_qid, target_qid=object_qid)
        for record in result:
            candidates.add(record)

    if session:
        exec_query(session, candidates)
    else:
        with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
            with driver.session(database=NEO4J_DB) as session:
                exec_query(session, candidates)

    return list(map(lambda x: (x['s'], x['p'], x['t']), candidates))


def create_neo4j_session() -> tuple[Driver, Session]:
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    return driver, driver.session(database=NEO4J_DB)


def close_neo4j_session(driver, session):
    if session:
        session.close()
    if driver:
        driver.close()


def fetch_edges_by_candidates(edge_candidates: list[tuple[str, str]], session=None) -> list[tuple[str, str, str]]:
    query = """UNWIND $candidates AS candidate
    MATCH (s:WikiEntity {entityName: candidate[0]})-[r:HAS_TYPE]->(t:WikiEntity {entityName: candidate[1]})
    RETURN s.entityName as s, r.type as p, t.entityName as t"""
    result = []

    def exec_query(session, edge_candidates):
        records = session.run(query, candidates=edge_candidates)
        for record in records:
            result.append((record['s'], record['p'], record['t']))

    if session:
        exec_query(session, edge_candidates)
    else:
        with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
            with driver.session(database=NEO4J_DB) as session:
                exec_query(session, edge_candidates)

    return result


def fetch_in_edges(wikidata_id: str) -> list[tuple[str, str, str]]:
    pass


def fetch_out_edges(wikidata_id: str) -> list[tuple[str, str, str]]:
    pass


def fetch_summaries(wikidata_id, session=None) -> list[tuple[str, str, str]] | None:
    # fetch the summary edges that has wikidata_id marked as summary_for
    query = """
        MATCH (s:WikiEntity)-[r:SUMMARY {summary_for: $wikidata_id}]->(t:WikiEntity)
        WHERE s.entityName = $wikidata_id OR t.entityName = $wikidata_id
        RETURN s.entityName AS s, r.predicate as p, t.entityName as t
    """
    result = []

    def exec_query(session, wikidata_id):
        records = session.run(query, wikidata_id=wikidata_id)
        for record in records:
            result.append((record['s'], record['p'], record['t']))

    if session:
        exec_query(session, wikidata_id)
    else:
        with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
            with driver.session(database=NEO4J_DB) as session:
                exec_query(session, wikidata_id)

    return result


def add_summary_edge(root_wikidata_id, from_entity, predicate, to_entity, session=None):
    # fetch the edge and append summary_for with root_wikidata_id as an attribute
    query = """
      MATCH (s:WikiEntity {entityName: $from_entity}), (t:WikiEntity {entityName: $to_entity})
        MERGE (s)-[r:SUMMARY {summary_for: $root_wikidata_id, predicate: $predicate}]->(t)
        RETURN s, r, t
    """

    def exec_query(session, from_entity, to_entity, root_wikidata_id, predicate):
        result = session.run(query, from_entity=from_entity, to_entity=to_entity, root_wikidata_id=root_wikidata_id,
                             predicate=predicate)
        return result.single()

    if session:
        exec_query(session, from_entity, to_entity, root_wikidata_id, predicate)
    else:
        with GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH) as driver:
            with driver.session(database=NEO4J_DB) as session:
                exec_query(session, from_entity, to_entity, root_wikidata_id, predicate)
