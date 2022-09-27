# -*- coding:utf-8 -*-
# @ModuleName: DataModel
# @Description: 
# @Author: laoweimin@corp.netease.com
# @Time: 2022/9/27 10:00


class MaterialItem(object):
	"""
	Use it to describe your Material
	"""
	def __init__(self, data):
		self.family = ""
		self.youngs = 0
		self.params = {}
		self.initFromData(data)

	def getMean(self, paramname: str):
		# a fake example
		for key, value in self.params.items():
			if key.startswith(paramname) and key.endswith("_mean"):
				return float(value)
		return 0

	def getStd(self, paramname: str):
		# a fake example
		for key, value in self.params.items():
			if key.startswith(paramname) and key.endswith("_sd"):
				return float(value)
		return 0

	def initFromData(self, data: dict):
		"""
		todo: data processing
		:param data:
		:return:
		"""
		self.params = data


class AshbyModel(object):
	def __init__(self, data: list):
		self._data = data
		self._items = []
		self.initFromData(data)

	def initFromData(self, data: list):
		# fake example, multiple lines in raw data could be one single item
		for item in data:
			matitem = MaterialItem(item)
			self._items.append(matitem)

	def getItem(self, index):
		return self._items[index]

	def getCount(self):
		return len(self._items)

