import os
import json

from abc import ABC, abstractmethod
from typing import Dict
from typing import List
from loguru import logger

class ConfigParser:

    @abstractmethod
    def check(self): pass

    @abstractmethod
    def parser(self): pass

class JsonConfigParser(ConfigParser):
    """
    Class to Parser Json condigurateion to dict
    """
    def __init__(self, path:str) -> None:
        
        self.path = path # path to json configuration

    def check(self) -> None:
        """
        Function to check configuration exist.
        """
        if os.path.exists(self.path):
            logger.info(f"Check configuration path: {self.path}: success.")
        else:
            raise FileNotFoundError(f"Input json file: {self.path} not exist.")
    
    def load(self):
        logger.info("Parser configuration to dict.")
        with open(self.path, 'r') as json_obj:
            json_config = json.load(json_obj)
        return json_config


