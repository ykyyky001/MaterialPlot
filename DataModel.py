# -*- coding:utf-8 -*-
import pandas as pd


class MaterialItem(object):
    """
    Use it to describe your Material
    """
    def __init__(self, data: pd.Series):
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

class MeanColor(object):
    def __init__(self, data: pd.Series):
        self.meanR = float(data["Color_R"])
        self.meanG = float(data["Color_G"])
        self.meanB = float(data["Color_B"])
        print("Family bubble has R ", self.meanR, ", G", self.meanG, ", B", self.meanB)


class AshbyModel(object):
    def __init__(self, filename: str):
        self.data = self.initFromData(filename)

    def initFromData(self, filename: str):
        # TODO(team) calculate case2 mean&std and fill in the table
        if filename:
            df = pd.read_csv(filename)
        else:
            df = pd.DataFrame()
        # remove na for compatibility now!
        df.dropna(inplace=True)
        return df
    
    @staticmethod
    def convertToItem(df):
        items = {}
        for idx, row in df.iterrows():
            items[row.Name] = MaterialItem(row)
        return items

    def getAllItems(self):
        return self.convertToItem(self.data)

    def getItem(self, label):
        return self.convertToItem(self.data[self.data.Name == label])

    def getItemsByFamily(self, column: str, label: str):
        return self.convertToItem(self.data[self.data[column]==label])

    def provideFamilyCandidateByColumn(self, column_name: str):
        candidate = self.data[column_name].drop_duplicates()
        return candidate.values

    def getCandidateColumns(self):
        # TODO(ky/tn): a more regulated filter for column candidates.
        return [column for column in self.data.columns if "Param" in column]

    def getCount(self):
        return len(self.data)

