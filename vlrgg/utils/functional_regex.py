def search_pattern(pattern, text):
    result = pattern.search(str(text))
    if result:
        return Ok(result[1])
    else:
        return Error(f'pattern {pattern} not found')
        

def re_match_group(group_name, re_match):
    pass
