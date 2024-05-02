from concurrent.futures import ThreadPoolExecutor, as_completed

from commons.storage import fetch_unprocessed_wikipedia_pages
from commons.wiki_entity import WikiEntity
from commons.wiki_mapping import WikiMapping


def process_row(wikipedia_id):
    WikiEntity(WikiMapping(wikipedia_id)).get_summaries(False)


if __name__ == '__main__':
    counter = 0
    with ThreadPoolExecutor(max_workers=4) as executor:
        while True:
            rows = fetch_unprocessed_wikipedia_pages()
            if not rows:
                print("No more rows to process.")
                break

            futures = [executor.submit(process_row, row[0]) for row in rows]

            for future in as_completed(futures):
                future.result()
