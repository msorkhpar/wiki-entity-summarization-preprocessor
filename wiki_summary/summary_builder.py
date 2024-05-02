from __future__ import annotations

from functools import lru_cache
from random import shuffle

import torch
from transformers import DistilBertTokenizer, DistilBertModel
import torch.nn.functional as F
import mwparserfromhell as mw

from commons.storage import fetch_predicate_metadata, fetch_wikipedia_page_content, add_summary_edge, \
    fetch_summaries, bulk_fetch_wikipedia_titles, fetch_edges_by_candidates, mark_wikipedia_page_processed
from commons.utils import dewiki

model = DistilBertModel.from_pretrained('distilbert-base-uncased')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')


@lru_cache(maxsize=256)
def _compute_embeddings(text):
    encoded_input = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=64)

    with torch.no_grad():
        return model(encoded_input['input_ids'])[0][:, 0, :]


def _pick_most_relevant_predicate(abstract_embedding, candidates: list[tuple[str, str, str]]) -> tuple[str, str, str]:
    shuffle(candidates)
    predicate_descriptions = [fetch_predicate_metadata(predicate) for _, predicate, _ in candidates]
    predicate_embeddings = torch.cat(
        [_compute_embeddings(f"{label}, {description}") for label, description in predicate_descriptions],
        dim=0)

    cos_similarities = F.cosine_similarity(abstract_embedding, predicate_embeddings, dim=1)

    return candidates[torch.argmax(cos_similarities).item()]


def _extract_abstract_and_mention_titles(content: str) -> tuple[str, list[str]]:
    def capitalize_first_letter(s: str) -> str:
        if not s:
            return s
        return s[0].upper() + s[1:]

    parser = mw.parse(content)
    abstract_section = str(parser.get_sections()[0])
    abstract_links = mw.parse(abstract_section).filter_wikilinks()
    filtered_links = list(
        filter(
            lambda page: not page.startswith(
                ("File:", "Category:", "Image:", "Help:", "Template:", "Portal:", "Special:", "Draft:", "Wikipedia:",
                 "WP:", "User:", "Talk:", "User_talk:", "Template_talk:", "Wikipedia_talk:", "File_talk:",
                 "MediaWiki_talk:", "MediaWiki:", "Module:", "Module_talk:", "Category_talk:", "Help_talk:",
                 "Draft_talk:", "TimedText:", "TimedText_talk:", "Book:", "Book_talk:",
                 "Education_Program:")
            ),
            [capitalize_first_letter(str(link.title).replace(" ", "_")) for link in abstract_links]
        )
    )
    return abstract_section, filtered_links


def _get_edge_candidates(root_wikidata_id, mentions: list[str]) -> dict[str, list[tuple[str, str, str]]] | None:
    """
    convert titles to wikidata ids and filter those that are in the graph
    :param root_wikidata_id:
    :param mentions:
    :return: {(from_entity_to_entity): [(from_entity, predicate_1, to_entity), (to_entity, predicate_1, from_entity),
    ..., (from_entity, predicate_2, to_entity)]}
    """
    if len(mentions) == 0:
        return None

    # convert wikipedia titles to wikidata ids
    neighbors = [meta[2] for neighbor, meta in bulk_fetch_wikipedia_titles(mentions).items()]

    edge_candidates = [(root_wikidata_id, neighbor) for neighbor in neighbors]
    edge_candidates += [(neighbor, root_wikidata_id) for neighbor in neighbors]
    # filter the edges that are already in Neo4j
    summary_edges = fetch_edges_by_candidates(edge_candidates)

    # group the edges that have the same from and to entities by predicates
    edge_candidates = {}
    for from_entity, predicate, to_entity in summary_edges:
        index = "_".join(sorted([from_entity, to_entity]))
        if index not in edge_candidates:
            edge_candidates[index] = []
        edge_candidates[index].append((from_entity, predicate, to_entity))
    return edge_candidates


def _create_abstract_embedding(raw_abstract: str):
    """
    clean the abstract and create an embedding
    :param raw_abstract:
    :return:
    """
    return _compute_embeddings(dewiki(raw_abstract))
    pass


def build_summaries(wikipedia_id, wikipedia_title, root_wikidata_id) -> list[tuple[str, str, str]]:
    """
    :param wikipedia_title:
    :param root_wikidata_id:
    :return: list of summaries: [ (from_entity, predicate, to_entity), ...]
    """
    # check if the summaries are already stored in Neo4j and return them
    summaries = fetch_summaries(root_wikidata_id)
    if summaries:
        return summaries
    else:
        summaries = []
    # if not stored, fetch page content, clean it, and store the mentioned in Neo4j
    page_content = fetch_wikipedia_page_content(wikipedia_title)
    if not page_content:
        return []
    raw_abstract, mentions = _extract_abstract_and_mention_titles(page_content)
    edge_candidates = _get_edge_candidates(root_wikidata_id, mentions)
    if not edge_candidates:
        return []
    abstract_embedding = None
    for index, candidates in edge_candidates.items():
        # if link is a single edge, just add the link, otherwise add the most relevant edge predicate
        if len(candidates) > 1:
            if abstract_embedding is None:
                abstract_embedding = _create_abstract_embedding(raw_abstract)
            candidate = _pick_most_relevant_predicate(abstract_embedding, candidates)
        else:
            candidate = candidates[0]
        add_summary_edge(root_wikidata_id, candidate[0], candidate[1], candidate[2])
        mark_wikipedia_page_processed(wikipedia_id)
        summaries.append(candidate)

    return summaries