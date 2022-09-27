class MaterialItem(object):
	"""
	Use it to describe your Material
	"""
	def __init__(self, data: dict):
		# TODO(team): update the names for their real meanings.
		self.x = float(data["Param2_mean"])
		self.y = float(data["Param3_mean"])
		self.w = float(data["Param2_sd"])
		self.h = float(data["Param3_sd"])
		self.label = data["Name"]
		self.color_r = int(data["Color_R"])
		self.color_g = int(data["Color_G"])
		self.color_b = int(data["Color_B"])
		#TODO(team): make sure the CSV column is consistent with this.
		if "rotation" in data.keys():
			self.rotation = data["rotation"]
		else:
			self.rotation = 0.0
		self.printDebugString()

	def printDebugString(self):
		print("Load ", self.label, ": ",
			  "x ", self.x, ", y ", self.y,
			  ", w ", self.w, ", h ", self.h,
			  ", rotation ", self.rotation)

class AshbyModel(object):
	def __init__(self, data: list):
		self.data = data
		self.items = {}
		self.initFromData(data)

	def initFromData(self, data: list):
		# TODO(team): adopt to the case when multiple lines in raw data could be one single item.
		for item in data:
			matitem = MaterialItem(item)
			self.items[matitem.label] = matitem

	def getAllItems(self):
		return self.items

	def getItem(self, label):
		if label in self.items.keys():
			return self.items[label]
		# else:
		# 	print("Do not have info about this material.")
		# 	return None

	def getCount(self):
		return len(self.items)

