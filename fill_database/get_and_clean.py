import os
import zipfile
from io import BytesIO

import requests
import pandas as pd
import numpy as np


BASE_DIR = os.path.dirname(__file__)
DOWNLOAD_URL = "https://bazaar.abuse.ch/export/csv/full/"
DATA_PATH = BASE_DIR + r"\data"

column_names = [
    '# "first_seen_utc"',
    'sha256_hash',
    'md5_hash',
    'sha1_hash',
    'file_type_guess',
    'mime_type',
    'signature'
]


def download_data():
    response = requests.get(DOWNLOAD_URL, stream=True)
    zip = zipfile.ZipFile(BytesIO(response.content))
    zip.extractall(DATA_PATH)


class DataCleaner:
    def __init__(self) -> None:

        data_file_path = DATA_PATH + r"\full.csv"
        self.data = pd.read_csv(data_file_path,
                                skiprows=8,
                                usecols=column_names
                                )
        self.data = self.data.replace("unknown", np.nan)
        self.data = self.data.dropna()

        self.data_cleaning()

    def data_cleaning(self):
        for column in self.data.columns[1:]:
            self.data[column] = self.data[column].map(self.cut)

    def cut(self, row):
        if isinstance(row, str):
            return row.strip().replace('"', '')
        else:
            return row

    def delivery(self):
        return self.data


if __name__ == "__main__":
    download_data()
