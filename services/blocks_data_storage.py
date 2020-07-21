import pandas as pd
import datetime as dt
from entities.patient_request import PatientRequest
import geopandas
import numpy as np
import logging
from scipy import spatial


class BlocksDataStorage:
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
        with open(self.__file_path, 'rb') as f:
            self.__dataframe = geopandas.read_file(f).to_crs(epsg='4326')
        self.__dataframe['LATITUDE'] = self.__dataframe['geometry'].centroid.y
        self.__dataframe['LONGITUDE'] = self.__dataframe['geometry'].centroid.x

    def assign_strata(self, patient: PatientRequest):
        logging.info(f"ckd-diagnosis-logger: assigning block strata")
        addresses_array = [patient.lat, patient.lng]
        blocks_array = self.__dataframe[['LATITUDE', 'LONGITUDE']].values

        strata_array = self.__dataframe[['ESTRATO']].values
        strata_array = np.vstack((strata_array, None))

        distances = spatial.cKDTree(blocks_array).query(addresses_array, 1, distance_upper_bound=0.0068, n_jobs=-1)
        patient.strata = strata_array[distances[1]][0]
