from parse import Extractor


html = """
<html>
    <body>
        <h1>   My First Heading</h1>
        <p>My first paragraph.</p>
        <div class="location"><html tag>123 fake street, Cleveland, OH 44123</div>
        <div class="location">456 fake street, Cleveland, OH 44123</div>
        <div class="location">789 fake street, Cleveland, OH 44123</div>
        <div id="id123">
            <span>hey my</span>
            &amp; dude,     the cost is &pound;420
        </div>
        <div class="same-price">$45.99</div>
        <div class="same-price">$46.99</div>
    </body>
</html>
"""

e = Extractor(html)

# regex_list = ["<(hey)><(dude)>"]
# regex_list = ["<([^>]*?)>"]
# regex_list = ["<h1>(.*?)</h1>"]
# regex_list = ["<div id=\"id123\">(.*?)</div>"]
#
# regex = r"""<div class="location">(.*?),\s+([^.]*?),\s+([A-Z]+)\s+(\d+)</div>"""

# regex = r"""<div class="location">(.*?)</div>"""
# regex = "salkdfjaljdfsjklsfjdldj"
# regex = "(<div)"
# regex = r"""<div class="same-price">(\$[\d.]+)</div>"""

selector = "div#id123"
selector_list = ["div.same-priceasdfasdf", "div.same-price"]
x = e.grab(selector_list=selector_list, element_name="my_variable", find_all=True)

# regex = r"""<div id="id123">(.*?)</div>"""
# x = e.grab(regex=regex, element_name="my_variable", allow_duplicates=True)


print(f"\n\nresult: {type(x).__name__}")
print(f"value: {x}")

