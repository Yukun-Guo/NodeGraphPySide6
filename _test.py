import types

inputPorts = [
    {
        "name": "'input1'",
        "multi_input": False,
        "display_name": "'Input 1'",
        "color": "(0, 0, 0)",
        "locked": False,
        "painter_func": "None",
    },
    {
        "name": "'input2'",
        "multi_input": False,
        "display_name": "'Input 2'",
        "color": "(0, 0, 0)",
        "locked": False,
        "painter_func": "None",
    },
]
outputPorts = [
    {
        "name": "'output1'",
        "multi_input": False,
        "display_name": "'Output 1'",
        "color": "(0, 0, 0)",
        "locked": False,
        "painter_func": "None",
    },
    {
        "name": "'output2'",
        "multi_input": False,
        "display_name": "'Output 2'",
        "color": "(0, 0, 0)",
        "locked": False,
        "painter_func": "None",
    },
]
elementDict = [
    {
        "type": "text_input",
        "name": "'text_input1'",
        "label": "'Text Input 1'",
        "placeholder_text": "'Enter text here'",
        "tooltip": "'This is a text input'",
        "tab": "'General'",
    },
    {
        "type": "combo_menu",
        "name": "'combo_menu1'",
        "label": "'Combo Menu 1'",
        "items": "['item1', 'item2', 'item3']",
        "tooltip": "'This is a combo menu'",
        "tab": "'General'",
    },
    {
        "type": "checkbox",
        "name": "'checkbox1'",
        "label": "'Checkbox 1'",
        "text": "'Check me'",
        "state": "False",
        "tooltip": "'This is a checkbox'",
        "tab": "'General'",
    },
]

code_str = "def __init__(self):\tsuper(DynamicNode, self).__init__()\n"
for inputPort in inputPorts:
    code_str = (
        code_str
        + f"\tself.add_input(name={inputPort['name']},"
        + f"multi_input={inputPort['multi_input']},"
        + f"display_name={inputPort['display_name']},"
        + f"color={inputPort['color']}, "
        + f"locked={inputPort['locked']},"
        + f"painter_func={inputPort['painter_func']})\n"
    )

for outputPort in outputPorts:
    code_str = (
        code_str
        + f"\tself.add_output(name={outputPort['name']},"
        + f"multi_input={outputPort['multi_input']},"
        + f"display_name={outputPort['display_name']},"
        + f"color={outputPort['color']}, "
        + f"locked={outputPort['locked']},"
        + f"painter_func={outputPort['painter_func']})\n"
    )

for element in elementDict:
    if element["type"] == "text_input":
        code_str = (
            code_str
            + f"\tself.add_text_input(name={element['name']},"
            + f"label={element['label']},"
            + f"placeholder_text={element['placeholder_text']},"
            + f"tooltip={element['tooltip']},"
            + f"tab={element['tab']})\n"
        )

    elif element["type"] == "combo_menu":
        code_str = (
            code_str
            + f"\tself.add_combo_menu(name={element['name']},"
            + f"label={element['label']},"
            + f"items={element['items']},"
            + f"tooltip={element['tooltip']},"
            + f"tab={element['tab']})\n"
        )

    elif element["type"] == "checkbox":
        code_str = (
            code_str
            + f"\tself.add_checkbox(name={element['name']},"
            + f"label={element['label']},"
            + f"text={element['text']},"
            + f"state={element['state']},"
            + f"tooltip={element['tooltip']},"
            + f"tab={element['tab']})\n"
        )
print(code_str)
# create_code = compile(
#         code_str,
#         "<string>",
#         "exec",
#     )


print(code_str)
