import os
import threading
import datetime

from ConfigParser import JsonConfigParser as ConfigParser
from Sink import PrometheusSink as Sink
from Monitor import SystemUsage as Monitor
from CustomException import FieldNotFoundError

from loguru import logger
from pprint import pprint
from typing import Callable

import pdb

class ProcessExporter:
    def __init__(self, pid: int, config_path: str, func_name: str) -> None:
        logger.info("Start monitor process info")
        logger.info("Parser configuration")

        self._stop_loop: bool = False
        self.pid: int = pid
        self.func_name:str = func_name

        config_parser = ConfigParser(config_path) # init config_parser
        config_parser.check()
        self.config = config_parser.load()

        self.monitor = Monitor(pid, self.config) # init monitor

        self.sink = Sink(self.config) # init sink
        self.sink.check()
    
    @logger.catch()
    def stop(self) -> None:
        self._stop_loop = True

    @logger.catch()
    def start(self) -> None:
        logger.info("Start get process information")
        while True:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = {"pid": self.pid, "function_name": self.func_name, "timestamp":timestamp}
            #for func in self.registered_monitor:
            for func in self.monitor.registered_monitor:
                result = {**result, **func()}
            self.sink.output(result)
            if self._stop_loop: break
