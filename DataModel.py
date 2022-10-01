# -*- coding:utf-8 -*-
import pandas as pd
from typing import List


class MaterialItem(object):
    """
    Use it to describe your Material
    """

    def __init__(self, data: pd.Series):
        self.x = float(data["Modulus_mean"])
        self.y = float(data["Strength_mean"])
        self.w = float(data["Modulus_sd"])
        self.h = float(data["Strength_sd"])
        self.label = data["Name"]
        self.color_r = int(data["Color_R"])
        self.color_g = int(data["Color_G"])
        self.color_b = int(data["Color_B"])
        self.family = data["Type"]
        if "rotation" in data.keys():
            self.rotation = data["rotation"]
        else:
            self.rotation = 0.0

    def printDebugString(self):
        print("Load ", self.label, ": ",
              "x ", self.x, ", y ", self.y,
              ", w ", self.w, ", h ", self.h,
              ", rotation ", self.rotation)


class AshbyModel(object):
    def __init__(self, filename: str):
        self.data = self.initFromData(filename)
        print(self.data)

    def getMaterialTypes(self):
        if "Type" not in self.data:
            return []
        return list(self.data["Type"].unique())

    def getItemByType(self, typestr: str):
        return self.getItemsByFamily("Type", typestr)

    def initFromData(self, filename: str):
        if filename:
            temp_df = pd.read_csv(filename)
            # Find the numerical and string columns.
            string_columns = []
            numeric_columns = []
            for column in temp_df.columns:
                if isinstance(temp_df[column][0], float):
                    numeric_columns.append(column)
                else:
                    string_columns.append(column)
            # Use the first column to group different samples from the same material.
            df = pd.DataFrame()
            for name, sub_df in temp_df.groupby(temp_df.columns[0]):
                # Calculate the mean among all numeric columns.
                avg_series = sub_df.loc[:, numeric_columns].mean(axis=0, skipna=True)
                # Take the first row to capture descriptive features in string columns.
                avg_series = avg_series.append(sub_df[string_columns].iloc[0].squeeze())
                df = df.append(avg_series.to_frame().T)

        else:
            df = pd.DataFrame()
        # remove na for compatibility now!
        df.dropna(inplace=True)
        return df

    def addProperty(self):
        self.data["Modulus/Density_mean"] = (self.data["Modulus_mean"] / self.data["Density"])
        self.data["Modulus/Density_sd"] = (self.data["Modulus_sd"] / self.data["Density"])
        print(self.data)

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
        return self.convertToItem(self.data[self.data[column] == label])

    def provideFamilyCandidateByColumn(self, column_name: str):
        candidate = self.data[column_name].drop_duplicates()
        return candidate.values

    def getCandidateColumns(self):
        # TODO(ky/tn): a more regulated filter for column candidates.
        return [column for column in self.data.columns if "Param" in column]

    def getCount(self):
        return len(self.data)

    @staticmethod
    def getMeanColor(items: List[MaterialItem]):
        sum_r = 0
        sum_g = 0
        sum_b = 0
        for item in items:
            r = item.color_r
            g = item.color_g
            b = item.color_b
            sum_r += r
            sum_g += g
            sum_b += b
        meanR = float(sum_r) / float(len(items))
        meanG = float(sum_g) / float(len(items))
        meanB = float(sum_b) / float(len(items))
        return meanR, meanG, meanB
