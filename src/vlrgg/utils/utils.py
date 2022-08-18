import numpy as np
from bs4 import BeautifulSoup
import requests
from expression import Ok, Result, Error
from expression.extra.result import pipeline
from expression.collections import seq

def scrape_url(strategy, url):
    url_pipe = pipeline(
                get_html,
                strategy)
    return url_pipe(url)


def get_html(url):
    events_resp = requests.get(url, timeout=10)
    if events_resp:
        return Ok(BeautifulSoup(events_resp.text, 'lxml'))
    else:
        return Error('Please check the URL of the webpage')


def sequence_iter(wrapped_iter):
    def sequence(value):
        match value:
            case Ok(value=val):
                return val
            case Error():
                return np.nan
    val = wrapped_iter.value
    match val:
        case seq.Seq() as l:
            seq_values = seq.of_iterable(l)
            return Ok(seq_values.filter(lambda x: x.is_ok()).map(sequence))
        case dict() as d:
            keys = list(d)
            wrapped_values = [d[k] for k in keys if k in d]
            unwrapped_values = map(sequence, wrapped_values)
            return Ok(dict(zip(keys, unwrapped_values)))
