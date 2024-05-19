from commons.storage import fetch_wiki_mapping


class WikiMapping:
    def __init__(self, wikipedia_id=None, wikipedia_page_title=None, wikidata_id=None):
        """
        :param wikipedia_id:
        :param wikipedia_page_title:
        :param wikidata_id:
        """
        if not wikipedia_page_title and not wikipedia_id and not wikidata_id:
            raise ValueError(
                'You must provide at least one wiki identifier wikipedia_page_title, wikipedia_id, or wikidata_id'
            )
        if wikipedia_id and wikipedia_page_title and wikidata_id:
            self.wikipedia_id, self.wikipedia_page_title, self.wikidata_id = wikipedia_id, wikipedia_page_title, wikidata_id
            return

        identifier = wikidata_id
        if not wikidata_id:
            if wikipedia_page_title:
                identifier = wikipedia_page_title
            else:
                identifier = wikipedia_id
        self.wikipedia_id, self.wikipedia_page_title, self.wikidata_id = fetch_wiki_mapping(
            identifier
        )
