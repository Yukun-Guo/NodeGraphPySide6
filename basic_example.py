#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import signal
import types
from PySide6 import QtCore, QtWidgets, QtGui

from NodeGraphQt import (
    NodeGraph,
    PropertiesBinWidget,
    NodesTreeWidget,
    NodesPaletteWidget,
)

# import example nodes from the "example_nodes" package
from examples.nodes import basic_nodes, custom_ports_node, group_node, widget_nodes
import PresetNotes
import inspect


def createCustomNode(
    nodeName: str,
    inputPorts: list,  # {'name': str,'multi_input':bool,'display_name':bool,'color':None,'locked':bool,'painter_func':None}=None,
    outputPorts: list,  # {'name': str,'multi_input':bool,'display_name':bool,'color':None,'locked':bool,'painter_func':None}=None,
    elementDict: list,  # {'type':str,'name': str, 'label': str, 'text': str, 'placeholder_text': str, 'tooltip':Any|None,'tab':Any|None}=None,
):
    # check if the node name is valid name for a class
    if not nodeName.isidentifier():
        raise ValueError("Invalid node name, must be a valid python class name")
    code_str = "def __init__(self):\n\tsuper(" + nodeName + ", self).__init__()\n"
    for inputPort in inputPorts:
        code_str = (
            code_str
            + f"\tself.add_input(name='{inputPort['name']}',"
            + f"multi_input={inputPort['multi_input']},"
            + f"display_name={inputPort['display_name']},"
            + f"color={inputPort['color']}, "
            + f"locked={inputPort['locked']},"
            + f"painter_func={inputPort['painter_func']})\n"
        )

    for outputPort in outputPorts:
        code_str = (
            code_str
            + f"\tself.add_output(name='{outputPort['name']}',"
            + f"multi_output={outputPort['multi_output']},"
            + f"display_name={outputPort['display_name']},"
            + f"color={outputPort['color']}, "
            + f"locked={outputPort['locked']},"
            + f"painter_func={outputPort['painter_func']})\n"
        )

    for element in elementDict:
        if element["type"] == "text_input":
            code_str = (
                code_str
                + f"\tself.add_text_input(name='{element['name']}',"
                + f"label='{element['label']}',"
                + f"placeholder_text='{element['placeholder_text']}',"
                + f"tooltip='{element['tooltip']}',"
                + f"tab='{element['tab']}')\n"
            )

        elif element["type"] == "combo_menu":
            code_str = (
                code_str
                + f"\tself.add_combo_menu(name='{element['name']}',"
                + f"label='{element['label']}',"
                + f"items={element['items']},"
                + f"tooltip='{element['tooltip']}',"
                + f"tab='{element['tab']}')\n"
            )

        elif element["type"] == "checkbox":
            code_str = (
                code_str
                + f"\tself.add_checkbox(name='{element['name']}',"
                + f"label='{element['label']}',"
                + f"text='{element['text']}',"
                + f"state={element['state']},"
                + f"tooltip='{element['tooltip']}',"
                + f"tab='{element['tab']}')\n"
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
            "__identifier__": "nodes.custom.",
            "NODE_NAME": nodeName,
            "__init__": func,
        },
    )

    return DynamicNode


class FlowNodeGraph(QtWidgets.QMainWindow):
    graph = None
    nodesTree = None

    def __init__(self):
        super(FlowNodeGraph, self).__init__()
        self.setAcceptDrops(True)
        self.initUI()
        self.properties_bin = PropertiesBinWidget(node_graph=self.graph)
        self.properties_bin.setWindowFlags(QtCore.Qt.WindowType.Tool)
        self.setupInitalGraphy()
        self.updateNodeExplorer()
        self.graph.node_double_clicked.connect(self.display_properties_bin)

    def dragEnterEvent(self, e):
        print("dragEnterEvent")
        e.accept()

    def dropEvent(self, e):
        super().dropEvent(e)
        position = e.position().toPoint()

        sender = e.source()
        selectedRows = sender.selectionModel().selectedRows()[0].row()

        # self.graph.create_node("nodes.basic.BasicNodeA", position=position)
        # The QTableWidget from which selected rows will be moved
        print(selectedRows)
        # print(sender)
        # Default dropEvent method fires dropMimeData with appropriate parameters (we're interested in the row index).

        print(position)
        e.accept()

    def initUI(self):
        # add menubar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("File")
        self.file_menu.addAction("New Node").triggered.connect(self.onCreateNode)

        # add status bar
        self.statusBar().showMessage("Ready")

        # create node graph.
        self.graph = NodeGraph()
        self.graph.set_context_menu_from_file("./examples/hotkeys/hotkeys.json")
        self.setCentralWidget(self.graph.widget)

        # create dock widgets Nodes Explorer.
        self.dockWidgetNoteExplorer = QtWidgets.QDockWidget("Nodes Explorer")
        nodeWidget = QtWidgets.QWidget()
        nodeWidgetLayout = QtWidgets.QVBoxLayout(
            nodeWidget, spacing=0, contentsMargins=QtCore.QMargins(0, 0, 0, 0)
        )
        nodefilter = QtWidgets.QLineEdit()
        nodefilter.setPlaceholderText("Filter nodes...")
        nodeWidgetLayout.addWidget(nodefilter)
        createNewNodeButton = QtWidgets.QPushButton("Create New Node")
        createNewNodeButton.clicked.connect(self.onCreateNode)
        nodeWidgetLayout.addWidget(createNewNodeButton)
        self.dockWidgetNoteExplorer.setWidget(nodeWidget)
        self.nodesTree = QtWidgets.QTreeWidget()
        self.nodesTree.setDragEnabled(True)
        self.nodesTree.setHeaderHidden(True)
        nodeWidgetLayout.addWidget(self.nodesTree)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidgetNoteExplorer
        )

        # create dock widgets Properties. TODO: Add the properties widget.
        self.dockWidgetProperties = QtWidgets.QDockWidget("Properties")
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidgetProperties
        )

    def updateNodeExplorer(self):
        self.nodesTree.clear()
        nodeClasses = inspect.getmembers(PresetNotes, inspect.isclass)
        # create tree widget items for each node class, each tree item has a icon and a text.
        for nodeClass in nodeClasses:
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, nodeClass[0])
            item.setIcon(
                0,
                QtGui.QIcon(
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "star.png")
                ),
            )
            self.nodesTree.addTopLevelItem(item)

    def setupInitalGraphy(self):
        # DynamicNode = createCustomNode(
        #     "DynamicNode",
        #     [
        #         {
        #             "name": "in A",
        #             "multi_input": False,
        #             "display_name": True,
        #             "color": None,
        #             "locked": False,
        #             "painter_func": None,
        #         }
        #     ],
        #     [
        #         {
        #             "name": "out A",
        #             "multi_output": False,
        #             "display_name": True,
        #             "color": None,
        #             "locked": False,
        #             "painter_func": None,
        #         }
        #     ],
        #     [
        #         {
        #             "type": "text_input",
        #             "name": "text_input",
        #             "label": "Text Input",
        #             "placeholder_text": "type here",
        #             "tooltip": None,
        #             "tab": None,
        #         },
        #         {
        #             "type": "combo_menu",
        #             "name": "combo_menu",
        #             "label": "Combo Menu",
        #             "items": ["item1", "item2", "item3"],
        #             "tooltip": None,
        #             "tab": None,
        #         },
        #         {
        #             "type": "checkbox",
        #             "name": "checkbox",
        #             "label": "",
        #             "text": "Check me",
        #             "state": True,
        #             "tooltip": None,
        #             "tab": None,
        #         },
        #     ],
        # )

        # registered example nodes.
        self.graph.register_nodes(
            [
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

        # create nodes.
        # n_dynamic = self.graph.create_node("nodes.custom.DynamicNode", text_color="#ffffff")

        # # create node with custom text color and disable it.
        # n_basic_a = self.graph.create_node("nodes.basic.BasicNodeA", text_color="#feab20")
        # n_basic_a.set_disabled(True)

        # # create node and set a custom icon.
        # n_basic_b = self.graph.create_node("nodes.basic.BasicNodeB", name="custom icon")
        # n_basic_b.set_icon(
        #     os.path.join(os.path.dirname(os.path.abspath(__file__)), "star.png")
        # )

        # create node with custom text color and disable it.
        n_basic_a = self.graph.create_node(
            "nodes.basic.BasicNodeA", text_color="#feab20"
        )
        n_basic_a.set_disabled(True)

        # create node and set a custom icon.
        n_basic_b = self.graph.create_node("nodes.basic.BasicNodeB", name="custom icon")
        n_basic_b.set_icon(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "star.png")
        )

        # create node with the custom port shapes.
        n_custom_ports = self.graph.create_node(
            "nodes.custom.ports.CustomPortsNode", name="custom ports"
        )

        # create node with the embedded QLineEdit widget.
        n_text_input = self.graph.create_node(
            "nodes.widget.TextInputNode", name="text node", color="#0a1e20"
        )

        # create node with the embedded QCheckBox widgets.
        n_checkbox = self.graph.create_node(
            "nodes.widget.CheckboxNode", name="checkbox node"
        )

        # create node with the QComboBox widget.
        n_combo_menu = self.graph.create_node(
            "nodes.widget.DropdownMenuNode", name="combobox node"
        )

        # crete node with the circular design.
        n_circle = self.graph.create_node("nodes.basic.CircleNode", name="circle node")

        # create group node.
        n_group = self.graph.create_node("nodes.group.MyGroupNode")

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
        self.graph.auto_layout_nodes()

        # crate a backdrop node and wrap it around
        # "custom port node" and "group node".
        n_backdrop = self.graph.create_node("Backdrop")
        n_backdrop.wrap_nodes([n_custom_ports, n_combo_menu])

        # fit nodes to the viewer.
        self.graph.clear_selection()
        self.graph.fit_to_selection()

        # Custom builtin widgets from NodeGraphQt
        # ---------------------------------------

    # example show the node properties bin widget when a node is double-clicked.
    def display_properties_bin(self):
        if not self.properties_bin.isVisible():
            self.properties_bin.show()

    @QtCore.Slot()
    def onCreateNode(self):
        QtWidgets.QInputDialog.getText(
            self,
            "Create Node",
            "Enter the name of the node you want to create",
            QtWidgets.QLineEdit.Normal,
            "",
        )
        # create a dialog to let user to create a new node.


if __name__ == "__main__":

    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    mainWin = FlowNodeGraph()
    mainWin.show()
    app.exec()
