# -*- coding:utf-8 -*-
from PySide2.QtWidgets import QTreeView
from .TreeModel import TreeItemModel
from PySide2.QtCore import Signal


class TreeView(QTreeView):
    OnSelectionChanged = Signal(list)

    def __init__(self, parent):
        super(TreeView, self).__init__(parent)
        self.model = TreeItemModel()
        self.setModel(self.model)
        self.setSelectionMode(QTreeView.ExtendedSelection)

    def getSelections(self):
        labels = []
        for index in self.selectedIndexes():
            labels.append(self.model.data(index))
        return labels

    def selectionChanged(self, selected, deselected):
        labels = self.getSelections()
        self.OnSelectionChanged.emit(labels)
        self.doItemsLayout()

    def clearModel(self):
        self.model.clear()

    def addFamilies(self, families):
        for family in families:
            self.model.addFamily(family)

    def addItem(self, item, family=None):
        self.model.addItemByFamily(item.label, family)
