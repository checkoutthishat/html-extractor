

class BlankInputSource(Exception):
    def __init__(self):
        message = "Input is blank."
        super().__init__(message)


class ElementNotFoundException(Exception):
    def __init__(self, element_name):
        if not element_name:
            element_name = "(unnamed)"
        message = f"Element \"{element_name}\" not found, but is required."
        super().__init__(message)


class NonDuplicateElementsFoundException(Exception):
    def __init__(self, element_name, first_element, second_element):
        if not element_name:
            element_name = "(unnamed)"
        message = f"Element \"{element_name}\" found non-duplicate entries: {first_element} -> {second_element}."
        super().__init__(message)


class MultipleElementsFoundException(Exception):
    def __init__(self, element_name, total_elements):
        if not element_name:
            element_name = "(unnamed)"
        message = f"Element \"{element_name}\" found {total_elements} elements, but `find_all` and `allow_duplicates` are False."
        super().__init__(message)


class ImproperlyConfiguredException(Exception):
    def __init__(self, is_empty=False):
        if is_empty:
            message = "Grab action is improperly configured, it contains neither RegEx(s) nor selector(s)."
        else:
            message = "Grab action is improperly configured, it contains both RegEx(s) and selector(s)."
        super().__init__(message)


class DataTypeMissMatchException(Exception):
    def __init__(self, value, expected):
        message = f"Failed to convert '{value}' to {expected}"
        super().__init__(message)
