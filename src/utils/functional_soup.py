from expression import Ok, Result, Error
from expression.collections import seq

def find_element(tag, attr, soup):
    element = soup.find(tag, attrs=attr)
    if element:
        return Ok(element)
    else:
        return Error(f'tag {tag} not found')

def find_elements(tag, attr, soup):
    elements = soup.find_all(tag, attrs=attr)
    if elements:
        return Ok(seq.of_iterable(elements))
    else:
        return Error(f'tag {tag} not found')

def attribute(attr, tag):
    try:
        value = tag[attr]
        return Ok(value)
    except KeyError as e:
        return Error(f'attribute {attr} not found')

def search_pattern(pattern, text):
    result = pattern.search(str(text))
    if result:
        return Ok(result[1])
    else:
        return Error(f'pattern {pattern} not found')
