import pandas as pd
import datetime as dt
from entities.dashboard_request import DashboardRequest
import numpy as np
import logging


class CKDDataStorage:
    def __init__(self, file_path: str, last_update: dt.datetime):
        self.__file_path = file_path
        self.__build_dataset()
        self.__last_update = last_update

    @property
    def last_update(self):
        return self.__last_update

    @last_update.setter
    def last_update(self, last_update: dt.datetime):
        self.__last_update = last_update

    @property
    def file_path(self):
        return self.__file_path

    @file_path.setter
    def file_path(self, file_path: str):
        self.__file_path = file_path

    def update(self):
        self.__build_dataset()

    def __build_dataset(self):
        self.__dataframe = pd.read_csv(self.__file_path)

    def build_pivot(self, dashboard: DashboardRequest):
        logging.info(f"ckd-diagnosis-logger: generating pivot table")
        genders = dashboard.genders
        years = dashboard.years
        values = dashboard.values
        indexes = dashboard.indexes
        columns = dashboard.columns
        group = dashboard.group
        filtered_table = self.__dataframe[(self.__dataframe['Sexo'].isin(genders)) &
                                          (self.__dataframe['Año'].isin(years))]
        if columns is None:
            names = indexes + values
        else:
            names = indexes + [str(i) for i in filtered_table[columns[0]].unique()]
        if group == 'sum':
            output_table = pd.pivot_table(filtered_table, values=values, index=indexes,
                                          aggfunc=np.sum, columns=columns).reset_index()
        else:
            if columns is not None:
                indexes_temporal = indexes + columns
            else:
                indexes_temporal = indexes
            if "Año" not in indexes:
                indexes_temporal = indexes_temporal + ['Año']
                output_temporal = pd.pivot_table(filtered_table, values=values, index=indexes_temporal,
                                                 aggfunc=np.sum).reset_index()
                output_table = pd.pivot_table(output_temporal, values=values,
                                              index=indexes, columns=columns).reset_index()
            else:
                output_table = pd.pivot_table(filtered_table, values=values, index=indexes,
                                              columns=columns).reset_index()
        output_table.columns = names
        output_table.fillna(0, inplace=True)
        return output_table
