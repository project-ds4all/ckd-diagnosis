import logging
import boto3
import re
import datetime as dt


class S3Service:

    def __init__(
            self,
            bucket: str,
            client: boto3.client
    ):
        self._client = client
        self._bucket = bucket

    def download_earliest_file(self, prefix, pattern, local_path) -> tuple:
        earliest_file_path = sorted(
            [content for content in self._client.list_objects(
                Bucket=self._bucket,
                Prefix=prefix)['Contents'] if re.match(pattern, content['Key'])],
            key=lambda x: x['LastModified'],
            reverse=True)[0]

        logging.info(f'Downloading {earliest_file_path["Key"]}')

        self._client.download_file(
            self._bucket,
            earliest_file_path['Key'],
            local_path
        )

        return local_path, dt.datetime.utcnow()
