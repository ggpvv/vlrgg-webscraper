from expression import Ok, Result, Error

def search_pattern(pattern, text):
    result = pattern.search(str(text))
    if result:
        return Ok(result)
    else:
        return Error(f'pattern {pattern} not found')
        

def re_match_group(group_name, re_match):
    try:
        group = re_match[group_name]
        return Ok(group)
    except IndexError as e:
        return Error(f'group {group_name} not found')
