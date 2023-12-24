import os

from abc import abstractmethod
from loguru import logger
import pdb

from typing import Dict
from typing import List
from typing import Union

import socket
from prometheus_client import Gauge, start_http_server
from CustomException import PrometheusSinkMetricNotFound

class Sink:
    
    @abstractmethod
    def check(self):
        """
        Method to check output folder exist
        """
        pass

    @abstractmethod
    def output(self):
        """
        Method to output data 
        """
        pass


class TextSink(Sink):

    def __init__(self, config) -> None:
        self.path = config.get("log_path")
        self.file_name = f"{self.path}/process_info.txt"

    def check(self) -> None:
         
        if os.path.isdir(self.path):
            logger.info(f"Input folder {self.path} is exist.")
        else:
            logger.warning(f"Input folder {self.path} is not exist.")
            logger.warning(f"Create folder: {self.path}.")
            os.makedirs(self.path)
    
    def output(self, file_name: str, data: Dict[str, Union[int, float]]) -> None:
        with open(self.file_name, 'a') as file_obj:
            file_obj.write(f"{data}\n")

class PrometheusSink(Sink):

    def __init__(self, config) -> None:
        self.host = config.get("host")
        self.port = config.get("port")
        self.metrics: Dict[str, Gauge] = dict()

        self.registered_metric("cpu_percent", "CPU usage of process", ["pid", "function_name"])
        self.registered_metric("memory_rss", "memory rss of process", ["pid", "function_name"])
        self.registered_metric("memory_vms", "memory vms of process", ["pid", "function_name"])

        for metric in config.get("monitors", []):
            self.registered_metric(metric, labels=["pid", "function_name"])


    def _port_not_available(self) -> bool:
        try:
            self.sock.connect((self.host, self.port))
            logger.warning(f"port :{self.port} has been use, try port {self.port + 1}.")
            return True
        except:
            logger.info(f"port: {self.port} is not in use.")
            return False

    def registered_metric(self, metric: str, desc: str=None, labels: List[str]=list()) -> None:
        if desc == None: desc = metric
        if len(labels) == 0:
            self.metrics[metric] = Gauge(metric, desc)
        else:
            self.metrics[metric] = Gauge(metric, desc, labels)

    def check(self) -> None:
        """
        Function to check port or other network is available.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)  # 設定超時時間（秒）
        logger.info(f"Check whether the specified port: {self.port} is available.")
        while self._port_not_available():
            self.port += 1
        
        start_http_server(addr=self.host, port=self.port)

    def output(self,data:Dict[str, Union[str, int, float]]) -> None: 

        pid = data.get("pid")
        function_name = data.get("function_name")
        for metric, gauge in self.metrics.items():
            value = data.get(metric)
            if gauge == None:
                raise PrometheusSinkMetricNotFound(f"Metric: {metric} did not monitor, result: {data}.")
            gauge.labels(pid, function_name).set(value)
