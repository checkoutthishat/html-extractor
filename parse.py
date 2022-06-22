import re

from pyquery import PyQuery as pq
from html import unescape

from exceptions import ElementNotFoundException, NonDuplicateElementsFoundException, MultipleElementsFoundException, \
    ImproperlyConfiguredException


class Extractor:
    def __init__(self, source):
        source = source.replace(r"&amp;", "&")
        source = source.replace(r"&nbsp;", " ")

        self.original_source = source
        self.action_source = None
        self.required = False
        self.allow_duplicates = False
        self.element_name = None
        self.find_all = False
        self.results = None
        self.minion = None
        self.action_type = None

    def grab(self, regex=None, regex_list=None, required=True, element_name=None, find_all=False, sanitize=True, allow_duplicates=False,
             selector=None, selector_list=None):
        action_type, actions = self._standardize_actions(regex, regex_list, selector, selector_list)

        self.required = required
        self.element_name = element_name
        self.find_all = find_all
        self.allow_duplicates = allow_duplicates
        self.action_type = action_type

        print(f"required: {required}")
        print(f"element_name: {element_name}")
        print(f"find_all: {find_all}")
        print(f"allow_duplicates: {allow_duplicates}")
        print(f"sanitize: {sanitize}")
        print(f"action_type: {action_type}")
        print()

        for action in actions:
            print(f"Testing {action_type} action: {action}")

            minion = Minion(self.action_source, action, required, element_name, action_type)
            minion.search()

            if minion.results:
                if sanitize:
                    minion.sanitize()
                self.minion = minion
                break

        self._validate_required()
        self._validate_find_all()
        self._validate_duplicates()

        return self._resolve()

    def _standardize_actions(self, regex, regex_list, selector, selector_list):
        if not regex_list and regex:
            regex_list = [regex]

        if not selector_list and selector:
            selector_list = [selector]

        if regex_list and selector_list:
            raise ImproperlyConfiguredException()

        if not regex_list and not selector_list:
            raise ImproperlyConfiguredException(True)

        if regex_list:
            self.action_source = self.original_source
            return "re", regex_list

        self.action_source = pq(self.original_source)
        return "pq", selector_list

    def _validate_duplicates(self):
        # Validation passes if `find_all` is True
        if self.find_all:
            return

        # Validation passes if there are no results or the number of elements are zero
        if not self.minion:
            return

        if not self.minion.multiple_rows_found:
            return

        # If the match action is a tuple of groups, return
        # ('hey my& dude, the cost is £420',)
        if isinstance(self.minion.results, tuple):
            return

        # [["<div"], ["<div"], ["<div"], ["<div"]]
        # [["123 fake street, Cleveland, OH 44123"], ["456 fake street, Cleveland, OH 44123"], ["789 fake street, Cleveland, OH 44123"]]
        # [["123 fake street", "Cleveland", "OH", "44123"], ["456 fake street", "Cleveland", "OH", "44123"], ["789 fake street", "Cleveland", "OH", "44123"]]

        values_dict = dict()
        for x, row in enumerate(self.minion.results):
            for y, cell in enumerate(row):
                if y not in values_dict:
                    values_dict[y] = cell
                    continue

                if values_dict[y] != cell:
                    raise NonDuplicateElementsFoundException(self.element_name, values_dict[y], cell)

    def _validate_required(self):
        if (not self.minion or not self.minion.results) and self.required:
            raise ElementNotFoundException(self.element_name)

    def _validate_find_all(self):
        if self.minion is None or self.minion.result_length == 0:
            return
        if self.minion.result_length > 1 and not self.find_all and not self.allow_duplicates:
            raise MultipleElementsFoundException(self.element_name, len(self.minion.results))

    def _resolve(self):
        # If there is no winning minion, return None
        if not self.minion:
            return None
        # If there is a winning minion, but it has no results, return None
        if self.minion.results is None:
            return None
        # If `find_all` isn't False, return the first element in the list
        if not self.find_all:
            return self.minion.results[0]
        # Finally, return the results
        return self.minion.results


class Minion:
    def __init__(self, source, action, required, element_name, action_type):
        self.source = source
        self.action = action
        self.required = required
        self.element_name = element_name
        self.action_type = action_type
        self.results = []
        self.result_length = 0
        self.multiple_rows_found = False

    def search(self):
        for i, match_object in enumerate(re.finditer(self.action, self.source, flags=re.I | re.S)):
            if i:
                self.multiple_rows_found = True
            self.results.append(match_object.groups())

        # ["<html tag>123 fake street, Cleveland, OH 44123", "456 fake street, Cleveland, OH 44123", "789 fake street, Cleveland, OH 44123"]
        # ["<span>hey my</span>& dude, the cost is &pound;420"]
        # [["<html tag>123 fake street", "Cleveland", "OH", "44123"], ["456 fake street", "Cleveland", "OH", "44123"], ["789 fake street", "Cleveland", "OH", "44123"]]
        self.result_length = len(self.results)

    def sanitize(self):
        sanitized_list = []

        for element in self.results:
            if isinstance(element, tuple):
                tuple_sanitized_list = []
                for sub_element in element:
                    tuple_sanitized_list.append(sanitize_html(sub_element))
                sanitized_list.append(tuple(tuple_sanitized_list))
            else:
                sanitized_list.append(sanitize_html(element))

        self.results = sanitized_list


def sanitize_html(html_str):
    if html_str is None:
        return

    # remove HTML
    html_str = re.sub(r"<\s*script[^>]*?>.*?<\s*/script\s*>", "", html_str, re.S | re.I)
    html_str = re.sub(r"<\s*style[^>]*?>.*?<\s*/style\s*>", "", html_str, re.S | re.I)
    html_str = re.sub(r"<[^>]+>", "", html_str, re.S | re.I)

    # remove leading/trailing spaces
    html_str = re.sub(r"^\s+|\s+$", "", html_str)

    # normalize double spacing
    html_str = re.sub(r"\s+", " ", html_str)

    # HTML entities
    html_str = unescape(html_str)

    return html_str

