from commons.wiki_mapping import WikiMapping
from wiki_summary.summary_builder import build_summaries
from commons.storage import fetch_wiki_mapping, fetch_predicate_metadata, fetch_first_neighbors, fetch_wikidata_metadata


class WikiEntity:
    def __init__(self, wiki_mapping: WikiMapping):
        '''
        :param wiki_mapping
        '''

        self.wikipedia_page_title = wiki_mapping.wikipedia_page_title
        self.wikipedia_id = wiki_mapping.wikipedia_id
        self.wikidata_id = wiki_mapping.wikidata_id
        self._abstract = None
        self._summaries = None
        self._wikidata_label = None
        self._wikidata_description = None

    def get_summaries(self, keep_results=True):
        if self._summaries:
            return self._summaries
        if not keep_results:
            build_summaries(self.wikipedia_id, self.wikipedia_page_title, self.wikidata_id)
            return
        self._summaries = build_summaries(self.wikipedia_id, self.wikipedia_page_title, self.wikidata_id)
        return self._summaries

    def get_detailed_summaries(self):
        if not self._summaries:
            self._summaries = self.get_summaries()
        results = []
        for summary in self._summaries:
            from_wikipedia_id, from_wikipedia_title, from_wikidata_id = fetch_wiki_mapping(summary[0])
            predicate_label, predicate_description = fetch_predicate_metadata(summary[1])
            to_wikipedia_id, to_wikipedia_title, to_wikidata_id = fetch_wiki_mapping(summary[2])
            result = {
                'from_entity': from_wikidata_id,
                'from_wikipedia_id': from_wikidata_id,
                'from_wikipedia_title': from_wikipedia_title,
                'predicate': summary[1],
                'predicate_label': predicate_label,
                'to_entity': to_wikidata_id,
                'to_wikipedia_id': to_wikipedia_id,
                'to_wikipedia_title': to_wikipedia_title,
            }
            results.append(result)
        return results

    # def get_abstract(self):
    #     if self._abstract:
    #         return self._abstract
    #     self._abstract = extract_cleaned_abstract(self.wikipedia_page_title)
    #     return self._summaries

    def get_in_edges(self):
        pass

    def get_out_edges(self):
        pass

    def get_first_hop(self):
        return fetch_first_neighbors(self.wikidata_id)

    def get_detailed_first_hop(self):
        neighbors = fetch_first_neighbors(self.wikidata_id)
        results = []
        for s, p, o in neighbors:
            results.append({
                'from': self.get_wikidata_label() if s == self.wikidata_id else fetch_wikidata_metadata(s)[0],
                'predicate': f"{fetch_predicate_metadata(p)[0]}({p})",
                'to': self.get_wikidata_label() if o == self.wikidata_id else fetch_wikidata_metadata(o)[0],
            })
        return results

    def get_wikidata_label(self):
        if self._wikidata_label:
            return self._wikidata_label
        self._wikidata_label, self._wikidata_description = fetch_wikidata_metadata(self.wikidata_id)
        return self._wikidata_label

    def get_wikidata_description(self):
        if self._wikidata_description:
            return self._wikidata_description
        self._wikidata_label, self._wikidata_description = fetch_wikidata_metadata(self.wikidata_id)
        return self._wikidata_description
