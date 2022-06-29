## Html Extractor
HTML extractor is a parsing module to help extract specific elements from HTML via [Regular Expressions](https://docs.python.org/3/library/re.html) (RegEx) and [PyQuery](https://pypi.org/project/pyquery/) (PQ, a third party [JQuery](https://jquery.com/) import) selectors, and avoid common pitfalls and parsing issues.

## Usage

### Ensure dependencies (PyQuery)
```pip3 install -r requirements.txt```

### Initiate the extractor class
```
from parse import Extractor

html = """<html><body><div id="id123">hey dude</div></body></html>"""
extractor = Extractor(html)
```
### Extract element from HTML
```
result = extractor.grab(selector="div#id123")
print(result)
> hey dude
```

See `example.py` for more exhaustive usage examples.

### Grab input variables
| Input | Default | Description |
| --- | ----------- | ----------- |
| `regex` | `None` | A single RegEx to match and extract elements. |
| `regex_list` | `[]` | A list of RegExs to match and extract elements. They are tried in order, when one succeeds, the rest are not tested. |
| `selector` | `None` | A single PyQuery selector to find and extract elements. |
| `selector_list` | `[]` | A list of PyQuery selector to find and extract elements. They are tried in order, when one succeeds, the rest are not tested. |
| `element_name` | `None` | The name of the field in jeopardy. Any exceptions raised during the extraction will tie this field name for easier debug. |
| `required` | `True` | Boolean to toggle whether an exception will be raised if the element is not found. |
| `find_all` | `False` | Boolean to denote if multiple elements are expected and should be returned. An exception will be raised if multiple elements are found and this is `False`. |
| `sanitize` | `True` | Boolean to gate whether or not the extracted elements should be sanitized.   |
| `allow_duplicates` | `False` | Boolean to toggle whether an exception will be raised if multiple non-duplicate elements are found. If `True` and all found elements are the same, the first element is returned. |
| `data_type` | `None` | Elements found must match this data type. All elements returned from both RegEx and PyQuery are `str`, but if this field is present, it will try to cast each element as that data type and raises an exception if it can not successfully cast it. |
| `custom_sanitize_method` | `None` | A method reference to your own custom sanitize method. This method will be invoked in lieu of (if `sanititze` is `False` or before (if `sanitize` is `True`) the normal sanitize method |

### Sanitize
During a grab action, if `sanitize` `True`, for every element and group found, it will:
1) remove script tags
2) remove style tags
3) remove any other HTML tags
4) remove leading/trailing spaces
5) normalize double spacing, i.e. replace all multiple spaces with a single space
6) unescape HTML entities 

### Exceptions
#### BlankInputSource
When instantiating the `Extractor` class, this exception will be raised if the input HTML is blank.  

#### ElementNotFoundException
During a `grab` action, if the element isn't found or is blank, this exception is raised. Unless `required` is `False`.

#### MultipleElementsFoundException
During a `grab` action, if `find_all` is `False` and multiple elements are found.

#### NonDuplicateElementsFoundException
During a `grab` action, if `find_all` is `False` and multiple elements are found, this exception will be raised if any of the elements aren't the exact same. This check happens _after_ the `MultipleElementsFoundException` check.


#### ImproperlyConfiguredException
During a `grab` action, this exception will be raised if the extraction attempt is invoked with _both_ a `regex` (or `regex_list`) and a `selector` (or `selector_list`).

#### DataTypeMissMatchException
During a `grab` action, if `data_type` is not `None` and an element fails to cast as that type, this exception is raised.