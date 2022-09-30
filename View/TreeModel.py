# -*- coding:utf-8 -*-
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt


class TreeItem(QStandardItem):
    def __init__(self, name):
        super(TreeItem, self).__init__(name)
        self.name = name

    def data(self, role: int):
        if role == Qt.DisplayRole:
            return self.name
        return super(TreeItem, self).data()


class TreeItemModel(QStandardItemModel):
    def __init__(self):
        super(TreeItemModel, self).__init__()
        self.rootitem = self.invisibleRootItem()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def addFamily(self, familyname):
        familyItem = TreeItem(familyname)
        self.appendRow(familyItem)
        return familyItem

    def addItemByFamily(self, label, family=None):
        if not family:
            item = TreeItem(label)
            self.appendRow(item)
            return item
        items = self.findItems(family, Qt.MatchRecursive)
        if not items:
            familyitem = self.addFamily(family)
        else:
            familyitem = items[0]
        item = TreeItem(label)
        familyitem.appendRow(item)
        return item
