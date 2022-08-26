from typing import List
from dataclasses import dataclass

from os import makedirs
from pathlib import Path

from tardis_client import TardisClient, Channel
from tardis_dev import datasets
import pandas as pd

@dataclass(frozen=True)
class DownloadParams:
    exchange : str
    date : str
    msg_type: str
    symbols : List[str]

@dataclass(frozen=True)
class DownloadRequest:
    params : DownloadParams
    cache_root_path: str
    api_key: str



class TardisGenerator:
    def __init__(self, request: DownloadRequest):
        self._build_cache_path(request)

        client = TardisClient(api_key=request.api_key, cache_dir=self.path)
        self.messages = client.replay(
            exchange = request.params.exchange,
            from_date = self._today_str(request.params.date),
            to_date = self._tomorrow_str(request.params.date),
            filters=[Channel(name=request.params.msg_type, symbols=request.params.symbols)],
        )

    # This could probably be simplified a bit
    def _build_cache_path(self, request: DownloadRequest):
        now = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        date_str = pd.Timestamp(request.params.date).strftime("%Y%m%d")
        new_cache_dir_lbl = request.params.exchange + date_str #+ "_" + now
        self.path = Path(request.cache_root_path) / new_cache_dir_lbl
        makedirs(self.path, exist_ok = True)

    def _today_str(self, date: str):
        return pd.Timestamp(date).strftime("%Y-%m-%d")

    def _tomorrow_str(self, date: str):
        return (pd.Timestamp(date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

class DatasetDownload:
    def __init__(self, request: DownloadRequest):
        datasets.download(
            exchange = request.params.exchange,
            data_types = [request.params.msg_type],
            from_date = self._today_str(request.params.date),
            to_date = self._tomorrow_str(request.params.date),
            symbols= request.params.symbols,
            api_key = request.api_key,
            download_dir = request.cache_root_path,
            get_filename= self._file_name
        )

    def _today_str(self, date: str):
        return pd.Timestamp(date).strftime("%Y-%m-%d")

    def _tomorrow_str(self, date: str):
        return (pd.Timestamp(date) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    def _file_name(self, exchange, data_type, date, symbol, format):
        return f"{exchange}_{symbol}_{date.strftime('%Y-%m-%d')}_{data_type}.{format}.gz"