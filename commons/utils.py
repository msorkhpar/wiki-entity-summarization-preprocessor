import re
import wikitextparser as wtp
from html2text import html2text as htt


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
