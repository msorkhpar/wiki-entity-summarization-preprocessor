from commons.wiki_mapping import WikiMapping
from wiki_summary.summary_builder import build_summaries
from commons.storage import fetch_wiki_mapping


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

    # def get_abstract(self):
    #     if self._abstract:
    #         return self._abstract
    #     self._abstract = extract_cleaned_abstract(self.wikipedia_page_title)
    #     return self._summaries

    def get_in_edges(self):
        pass

    def get_out_edges(self):
        pass

    def get_wikidata_label(self):
        if self._wikidata_label:
            return self._wikidata_label
        self._wikidata_label, self._wikidata_description = fetch_wiki_mapping(self.wikidata_id)

    def get_wikidata_description(self):
        if self._wikidata_description:
            return self._wikidata_description
        self._wikidata_label, self._wikidata_description = fetch_wiki_mapping(self.wikidata_id)
