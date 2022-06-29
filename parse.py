import re

from pyquery import PyQuery as pq
from html import unescape

from exceptions import ElementNotFoundException, NonDuplicateElementsFoundException, MultipleElementsFoundException, \
    ImproperlyConfiguredException, DataTypeMissMatchException


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
        self.data_type = None
        self.custom_sanitize_method = None

    def grab(self, regex=None, regex_list=None, required=True, element_name=None, find_all=False, sanitize=True, allow_duplicates=False,
             selector=None, selector_list=None, data_type=None, custom_sanitize_method=None):
        action_type, actions = self._standardize_actions(regex, regex_list, selector, selector_list)

        self.required = required
        self.element_name = element_name
        self.find_all = find_all
        self.allow_duplicates = allow_duplicates
        self.action_type = action_type
        self.data_type = data_type
        self.custom_sanitize_method = custom_sanitize_method

        # print(f"required: {required}")
        # print(f"element_name: {element_name}")
        # print(f"find_all: {find_all}")
        # print(f"allow_duplicates: {allow_duplicates}")
        # print(f"sanitize: {sanitize}")
        # print(f"action_type: {action_type}")
        # print(f"data_type: {data_type}")
        # if custom_sanitize_method:
        #     print(f"custom_sanitize_method: {custom_sanitize_method.__name__}")
        # print()

        for action in actions:
            # print(f"Testing {action_type} action: {action}\n")

            minion = Minion(self.action_source, action, required, element_name, action_type)
            minion.search()

            if minion.results:
                if sanitize:
                    minion.sanitize(self.custom_sanitize_method)
                self.minion = minion
                break

        self._validate_required()
        self._validate_find_all()
        self._validate_duplicates()
        self._validate_data_types()

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

    def _validate_data_types(self):
        if not self.data_type:
            return

        validated_results = []
        for row in self.minion.results:
            validated_row = ()
            for cell in row:
                exception = None
                try:
                    validated_row += (self.data_type(cell), )
                except ValueError as e:
                    exception = DataTypeMissMatchException(cell, self.data_type.__name__)
                if exception:
                    raise exception

            validated_results.append(validated_row)

        self.minion.results = validated_results

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

        # PQ
        if self.action_type == "pq":
            distinct_set = set(self.minion.results)
            if len(distinct_set) != 1:
                distinct_list = list(distinct_set)
                value_a = distinct_list[0]
                value_b = distinct_list[1]
                raise NonDuplicateElementsFoundException(self.element_name, value_a, value_b)

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

        minion = self.minion
        self.minion = None

        # If `find_all` isn't False, return the first element in the list
        if not self.find_all:
            row = minion.results[0]
            if len(row) == 1:
                return row[0]
            return row

        # Finally, return the results
        resolved_list = []
        for row in minion.results:
            if len(row) != 1:
                return minion.results
            resolved_list.append(row[0])

        return resolved_list


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
        if self.action_type == "re":
            result_set = re.finditer(self.action, self.source, flags=re.I | re.S)
        else:
            result_set = self.source.items(self.action)

        for i, match_object in enumerate(result_set):
            if i:
                self.multiple_rows_found = True

            if self.action_type == "re":
                self.results.append(match_object.groups())
            else:
                self.results.append([match_object, ])

        self.result_length = len(self.results)

    def sanitize(self, custom_sanitize_method=None):
        sanitized_list = []

        for element in self.results:
            if isinstance(element, (tuple, list)):
                tuple_sanitized_list = []
                for sub_element in element:
                    if isinstance(sub_element, pq):
                        if custom_sanitize_method:
                            tuple_sanitized_list.append(custom_sanitize_method(sanitize_html(sub_element.html())))
                        else:
                            tuple_sanitized_list.append(sanitize_html(sub_element.html()))
                    else:
                        if custom_sanitize_method:
                            tuple_sanitized_list.append(custom_sanitize_method(sanitize_html(sub_element)))
                        else:
                            tuple_sanitized_list.append(sanitize_html(sub_element))
                sanitized_list.append(tuple(tuple_sanitized_list))
            elif isinstance(element, pq):
                if custom_sanitize_method:
                    sanitized_list.append(custom_sanitize_method(sanitize_html(element.html())))
                else:
                    sanitized_list.append(sanitize_html(element.html()))
            else:
                if custom_sanitize_method:
                    sanitized_list.append(custom_sanitize_method(sanitize_html(element)))
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

