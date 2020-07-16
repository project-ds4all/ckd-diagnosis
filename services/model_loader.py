import logging
import joblib

from services.ckd_predictor import ModelType


class ModelLoader:
    def __init__(self,
                 path: str):
        self.__path = path
        self.model = None

    def load(self) -> ModelType:
        logging.info(f'Loading Pickle file: {self.__path}')
        try:
            with(open(self.__path, 'rb')) as binary:
                self.model = joblib.load(binary)
                logging.info(f'Pickle file: {self.__path} loaded')
        except FileNotFoundError:
            raise FileNotFoundError(f'Pickle file {self.__path} not found')

        return self.model

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, path: str) -> None:
        self.__path = path

