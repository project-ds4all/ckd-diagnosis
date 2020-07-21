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
        group = dashboard.group
        filtered_table = self.__dataframe[(self.__dataframe['Sexo'].isin(genders)) &
                                          (self.__dataframe['Año'].isin(years))]
        if group == 'sum':
            output_table = pd.pivot_table(filtered_table, values=values, index=indexes,
                                          aggfunc=np.sum).reset_index()
        else:
            indexes_temporal = indexes + ['Año']
            output_temporal = pd.pivot_table(filtered_table, values=values, index=indexes_temporal,
                                             aggfunc=np.sum).reset_index()
            output_table = pd.pivot_table(output_temporal, values=values, index=indexes).reset_index()

        return output_table
