#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import signal
import types
from PySide6 import QtCore, QtWidgets

from NodeGraphQt import (
    NodeGraph,
    PropertiesBinWidget,
    NodesTreeWidget,
    NodesPaletteWidget,
)

# import example nodes from the "example_nodes" package
from examples.nodes import basic_nodes, custom_ports_node, group_node, widget_nodes


def createCustomNode(
    nodeName: str,
    inputPorts: list,  # {'name': str,'multi_input':bool,'display_name':bool,'color':None,'locked':bool,'painter_func':None}=None,
    outputPorts: list,  # {'name': str,'multi_input':bool,'display_name':bool,'color':None,'locked':bool,'painter_func':None}=None,
    elementDict: list,  # {'type':str,'name': str, 'label': str, 'text': str, 'placeholder_text': str, 'tooltip':Any|None,'tab':Any|None}=None,
):
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

    create_code = compile(
        code_str,
        "<string>",
        "exec",
    )
    func = types.FunctionType(create_code.co_consts[0], globals(), "func")

    # dynamically define a node class based on BaseNode.
    DynamicNode = type(
        nodeName,
        (basic_nodes.BaseNode,),
        {
            "__identifier__": "nodes." + nodeName.toLowerCase(),
            "NODE_NAME": nodeName,
            "__init__": func,
        },
    )

    return DynamicNode


if __name__ == "__main__":

    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = NodeGraph()

    # set up context menu for the node graph.
    graph.set_context_menu_from_file("./examples/hotkeys/hotkeys.json")

    ######################################################################
    # dynamically create a function and execute it.
    DynamicNode = createCustomNode(
        "DynamicNode",
        [
            {
                "name": "in A",
                "multi_input": False,
                "display_name": True,
                "color": None,
                "locked": False,
                "painter_func": None,
            }
        ],
        [
            {
                "name": "out A",
                "multi_input": False,
                "display_name": True,
                "color": None,
                "locked": False,
                "painter_func": None,
            }
        ],
        [
            {
                "type": "text_input",
                "name": "text_input",
                "label": "Text Input",
                "placeholder_text": "type here",
                "tooltip": None,
                "tab": None,
            },
            {
                "type": "combo_menu",
                "name": "combo_menu",
                "label": "Combo Menu",
                "items": ["item1", "item2", "item3"],
                "tooltip": None,
                "tab": None,
            },
            {
                "type": "checkbox",
                "name": "checkbox",
                "label": "Checkbox",
                "text": "Check me",
                "state": True,
                "tooltip": None,
                "tab": None,
            },
        ],
    )

    ######################################################################
    # registered example nodes.
    graph.register_nodes(
        [
            DynamicNode,
            basic_nodes.BasicNodeA,
            basic_nodes.BasicNodeB,
            basic_nodes.CircleNode,
            custom_ports_node.CustomPortsNode,
            group_node.MyGroupNode,
            widget_nodes.DropdownMenuNode,
            widget_nodes.TextInputNode,
            widget_nodes.CheckboxNode,
        ]
    )

    # show the node graph widget.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.show()

    # create nodes.
    n_dynamic = graph.create_node("nodes.dyBasic.DynamicNode", text_color="#feabf0")

    # create node with custom text color and disable it.
    n_basic_a = graph.create_node("nodes.basic.BasicNodeA", text_color="#feab20")
    n_basic_a.set_disabled(True)

    # create node and set a custom icon.
    n_basic_b = graph.create_node("nodes.basic.BasicNodeB", name="custom icon")
    n_basic_b.set_icon(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "star.png")
    )

    # create node with the custom port shapes.
    n_custom_ports = graph.create_node(
        "nodes.custom.ports.CustomPortsNode", name="custom ports"
    )

    # create node with the embedded QLineEdit widget.
    n_text_input = graph.create_node(
        "nodes.widget.TextInputNode", name="text node", color="#0a1e20"
    )

    # create node with the embedded QCheckBox widgets.
    n_checkbox = graph.create_node("nodes.widget.CheckboxNode", name="checkbox node")

    # create node with the QComboBox widget.
    n_combo_menu = graph.create_node(
        "nodes.widget.DropdownMenuNode", name="combobox node"
    )

    # crete node with the circular design.
    n_circle = graph.create_node("nodes.basic.CircleNode", name="circle node")

    # create group node.
    n_group = graph.create_node("nodes.group.MyGroupNode")

    # make node connections.

    # (connect nodes using the .set_output method)
    n_text_input.set_output(0, n_custom_ports.input(0))
    n_text_input.set_output(0, n_checkbox.input(0))
    n_text_input.set_output(0, n_combo_menu.input(0))

    # (connect nodes using the .set_input method)
    n_group.set_input(0, n_custom_ports.output(1))
    n_basic_b.set_input(2, n_checkbox.output(0))
    n_basic_b.set_input(2, n_combo_menu.output(1))

    # (connect nodes using the .connect_to method from the port object)
    # n_basic_a.input(0).connect_to(n_basic_b.output(0))
    n_basic_b.output(0).connect_to(n_basic_a.input(0))

    # auto layout nodes.
    graph.auto_layout_nodes()

    # crate a backdrop node and wrap it around
    # "custom port node" and "group node".
    n_backdrop = graph.create_node("Backdrop")
    n_backdrop.wrap_nodes([n_custom_ports, n_combo_menu])

    # fit nodes to the viewer.
    graph.clear_selection()
    graph.fit_to_selection()

    # Custom builtin widgets from NodeGraphQt
    # ---------------------------------------

    # create a node properties bin widget.
    properties_bin = PropertiesBinWidget(node_graph=graph)
    properties_bin.setWindowFlags(QtCore.Qt.Tool)

    # example show the node properties bin widget when a node is double-clicked.
    def display_properties_bin(node):
        if not properties_bin.isVisible():
            properties_bin.show()

    # wire function to "node_double_clicked" signal.
    graph.node_double_clicked.connect(display_properties_bin)

    # create a nodes tree widget.
    nodes_tree = NodesTreeWidget(node_graph=graph)
    nodes_tree.set_category_label("nodeGraphQt.nodes", "Builtin Nodes")
    nodes_tree.set_category_label("nodes.custom.ports", "Custom Port Nodes")
    nodes_tree.set_category_label("nodes.widget", "Widget Nodes")
    nodes_tree.set_category_label("nodes.basic", "Basic Nodes")
    nodes_tree.set_category_label("nodes.group", "Group Nodes")
    # nodes_tree.show()

    # create a node palette widget.
    nodes_palette = NodesPaletteWidget(node_graph=graph)
    nodes_palette.set_category_label("nodeGraphQt.nodes", "Builtin Nodes")
    nodes_palette.set_category_label("nodes.custom.ports", "Custom Port Nodes")
    nodes_palette.set_category_label("nodes.widget", "Widget Nodes")
    nodes_palette.set_category_label("nodes.basic", "Basic Nodes")
    nodes_palette.set_category_label("nodes.group", "Group Nodes")
    # nodes_palette.show()

    app.exec()
