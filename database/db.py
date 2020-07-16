import logging
from flask_sqlalchemy import BaseQuery
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import StatementError
from time import sleep
from flask_sqlalchemy import SQLAlchemy

import settings


class RetryingQuery(BaseQuery):
    __retry_count__ = 3
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __iter__(self):
        attempts = 0
        while True:
            attempts += 1
            try:
                return super().__iter__()
            except OperationalError as ex:
                if "server closed the connection unexpectedly" not in str(ex):
                    raise
                if attempts < self.__retry_count__:
                    sleep_for = 2 ** (attempts - 1)
                    logging.error(
                        "Database connection error: {} - sleeping for {}s"
                        " and will retry (attempt #{} of {})".format(
                            ex, sleep_for, attempts, self.__retry_count__
                        )
                    )
                    sleep(sleep_for)
                    continue
                else:
                    raise
            except StatementError as ex:
                if "reconnect until invalid transaction is rolled back" not in str(ex):
                    raise
                self.session.rollback()


db = SQLAlchemy(query_class=RetryingQuery)

connection_uri = 'postgres://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}'.format(
    PG_USER=settings.PG_USER,
    PG_PASSWORD=settings.PG_PASSWORD,
    PG_HOST=settings.PG_HOST,
    PG_PORT=settings.PG_PORT,
    PG_DATABASE=settings.PG_DATABASE
)
