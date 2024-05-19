import re
from functools import lru_cache

import wikitextparser as wtp
from html2text import html2text as htt
import mwparserfromhell as mw
import torch
from transformers import DistilBertTokenizer, DistilBertModel


def basic_replacements(text):
    replacements = [
        ('&lt;', '<'),
        ('&gt;', '>'),
        ('&quot;', '"'),
        ("'''", ' = '),
        ("'{2,}", ''),
        ('\n', ' '),
        (r'\n', ' '),
        ('\\n', ' '),
        ('r\\n', ' '),
        ('<ref.*?>', ''),
        ('</ref>', ''),
        ('http.*?\s', ''),
        ('\s+', ' '),
    ]
    text = text.replace('\\n', ' ')
    for r in replacements:
        text = re.sub(r[0], r[1], text)
    return text


def remove_double_curly(text):
    while True:
        before = len(text)
        text = re.sub('', '', text)
        after = len(text)
        if before == after:
            return text


def remove_double_brackets(text):
    while True:
        before = len(text)
        double_brackets = re.findall('\[\[.*?\]\]', text)
        for db in double_brackets:
            if '|' in db:
                new = db.split('|')[-1].strip(']')
                text = text.replace(db, new)
            else:
                new = db.strip('[').strip(']')
                text = text.replace(db, new)
        after = len(text)
        if before == after:
            return text


# https://daveshap.github.io/DavidShapiroBlog/automation/2020/11/24/parsing-all-wikipedia.html
def dewiki(text):
    text = remove_double_curly(text)  # Remove most
    text = remove_double_brackets(text)  # Remove most [[ ]]
    text = wtp.parse(text).plain_text()  # parse out MediaWiki
    text = htt(text)  # parse out any residual HTML
    text = text.replace('\\n', ' ')  # replace any newlines with single space
    text = re.sub('\[\[', ' ', text)  # remove any remnant [[
    text = re.sub('\]\]', ' ', text)  # remove any remnant ]]
    text = re.sub('\s+', ' ', text)  # condense excess whitespace into a single space
    return text


def extract_mention_titles(raw_abstract: str) -> list[str]:
    def capitalize_first_letter(s: str) -> str:
        if not s:
            return s
        return s[0].upper() + s[1:]

    abstract_links = mw.parse(raw_abstract).filter_wikilinks()
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
    return filtered_links


def extract_raw_abstract(content: str) -> str:
    parser = mw.parse(content)
    abstract_section = str(parser.get_sections()[0])
    return abstract_section


model = DistilBertModel.from_pretrained('distilbert-base-uncased')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')


@lru_cache(maxsize=256)
def compute_embeddings(text):
    encoded_input = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=64)

    with torch.no_grad():
        return model(encoded_input['input_ids'])[0][:, 0, :]
