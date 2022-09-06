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
        
        
def inner_text(soup):
    text = soup.get_text(' ', strip=True)
    if text is not None:
        return Ok(text)
    else:
        return Error('no inner text for provided html element')

    
def stripped_strings(soup):
    strings = [text for text in soup.stripped_strings]
    if strings:
        return Ok(strings)
    else:
        return Error('no inner text for provided html element')
         
