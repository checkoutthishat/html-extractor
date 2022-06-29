import traceback

from parse import Extractor
from exceptions import ElementNotFoundException


html = """
<html>
    <body>
        <h1>   My First Heading</h1>
        <p>My first paragraph.</p>
        <div class="location"><html-tag>123 fake street, Cleveland, OH 44123</div>
        <div class="location">456 fake street, Cleveland, OH 44123</div>
        <div class="location">789 fake street, Cleveland, OH 44123</div>
        Quantity: <span id="product-quantity">44</span>
        <div id="id123">
            <span>hey my</span>
            &amp; dude,     the cost is &pound;420
        </div>
        <div class="same-price">$45.99</div>
        <div class="same-price">$45.99</div>
        <div class="different-price">$29.49</div>
        <div class="different-price">$35.01</div>
        <span id="secret-price">**1,123**</span>
    </body>
</html>
"""

extractor = Extractor(html)

print("single element, PyQuery")
result = extractor.grab(selector="span#product-quantity")
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# single element, RegEx")
result = extractor.grab(regex=r"dude,\s*the cost is &pound;(\d+)")
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# single element, RegEx list")
regex_list = [
    r"this text doesn't exist so it won't be found",  # this won't be found
    r"dude,\s*the cost is &pound;(\d+)",
]
result = extractor.grab(regex_list=regex_list)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# single element, PyQuery list")
selector_list = [
    "div#id8675309",  # this won't be found
    "div#id123",
]
result = extractor.grab(selector_list=selector_list)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# multiple groups, RegEx")
result = extractor.grab(regex=r"""<html-tag>\s*([^>]*?),\s*([^>]*?),\s*([A-Z]{2})\s*(\d+)</div>""")
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# multiple elements, RegEx")
result = extractor.grab(regex=r"""<div class="location">(.*?)</div>""", find_all=True)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# multiple elements, PyQuery")
result = extractor.grab(selector="div.location", find_all=True)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# multiple elements and multiple groups, RegEx")
result = extractor.grab(regex=r"""<div class="location">\s*([^>]*?),\s*([^>]*?),\s*([A-Z]{2})\s*(\d+)</div>""", find_all=True)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# allowing duplicate elements, PyQuery")
result = extractor.grab(selector="div.same-price", allow_duplicates=True)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")


def custom_sanitize_method(result_string):
    result_string = result_string.replace("**", "")
    return result_string


print("# custom sanitize method, PyQuery")
result = extractor.grab(selector="span#secret-price", custom_sanitize_method=custom_sanitize_method)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")


def custom_sanitize_method2(result_string):
    result_string = result_string.replace("**", "").replace(",", "")
    return result_string


print("# custom sanitize method and data type enforcement, PyQuery")
result = extractor.grab(selector="span#secret-price", data_type=int, custom_sanitize_method=custom_sanitize_method2)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# non-required element")
result = extractor.grab(regex=r"this text does not show up in the html", required=False)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# data type enforcement")
result = extractor.grab(regex=r"dude,\s*the cost is &pound;(\d+)", data_type=int)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# toggle sanitize off")
result = extractor.grab(selector="div#id123", sanitize=False)
print(f"data type: {type(result).__name__}")
print(f"result: {result}\n")

print("# add element name for debugging")
try:
    result = extractor.grab(selector="div#12341341341135", element_name="my-element-name")
except ElementNotFoundException as e:
    traceback.print_exc()
