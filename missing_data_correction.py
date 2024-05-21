import csv

import pandas as pd
import wptools

from commons.storage import insert_missing_mappings
from commons.wiki_entity import WikiEntity
from commons.wiki_mapping import WikiMapping


def fetch_wikidata_id(title):
    try:
        page = wptools.page(title, silent=True).get(show=False)
        wikidata_id = page.data['wikibase']
        return wikidata_id
    except Exception as e:
        return None


if __name__ == '__main__':
    csv_file = 'missing_data_pages.csv'
    df = pd.read_csv(csv_file)
    result = []
    failed = []
    insert_queries = []
    for index, row in df.iterrows():
        page_id = row['id']
        title = row['title']
        wikidata_id = fetch_wikidata_id(title)
        insert_missing_mappings(page_id, title, wikidata_id)
        if wikidata_id:
            WikiEntity(WikiMapping(wikidata_id=wikidata_id)).get_summaries(False)
