import json

def escape_for_js(text):
    """
    Safely escape a string for use in JavaScript.
    Handles quotes, backslashes, newlines, and other special characters.
    """
    if text is None:
        return 'null'
    
    # Convert to string and handle NaN/null values
    text = str(text)
    if text.lower() in ['nan', 'none', 'null']:
        return 'null'
    
    # Use JSON encoding which properly escapes all special characters
    return json.dumps(text)

def dict_to_js_object(d):
    """
    Convert a Python dictionary to a JavaScript object string with proper escaping.
    """
    js_pairs = []
    for key, value in d.items():
        escaped_key = escape_for_js(str(key))
        escaped_value = escape_for_js(str(value))
        js_pairs.append(f"{escaped_key}: {escaped_value}")
    
    return "{" + ", ".join(js_pairs) + "}"