import psutil
import sh
import os

from loguru import logger
from typing import Dict
from typing import Union

class SystemUsage:
    """
    System usage monitor.
    """
    def __init__(self, pid: int, config: Dict[str, Union[str, int]], unit: str="MB") -> None:
        """
        :param pid:
            - desc: process ID,
        :param config:
            - desc: configuration.
        :param unit:
            - desc: unit of memory and folfer size.
        """
        self.pid = pid
        self.config = config
        self.interval = self.config.get("interval", 15)
        self.process_info = psutil.Process(pid)
        self.unit = unit

        self.monitors = {
            "cpu_percent": self.get_cpu_percent,
            "memory_info": self.get_memory_info,
            "folder_size": self.get_folder_size
        }

        self.registered_monitor = list()

        self._register("cpu_percent")
        self._register("memory_info")

        self.targets = self.config.get("monitors", [])

        for target in self.targets:
            self._register(target)

    def _register(self, target: str) -> None:
        """
        Function to register monitor to monitoring list.
        """
        logger.info(f"Register exporter of {target}")
        func = self.monitors.get(target)
        if func:
            self.registered_monitor.append(func)
        else:
            raise KeyError(f"Can not found input monitor target: {target} in all exporters")

    
    def get_cpu_percent(self) -> Dict[str, str]:
        """
        Function to monitor process cpu percentage.
        """
        cpu_percent = self.process_info.cpu_percent(interval=self.interval)
        return {"cpu_percent": cpu_percent}

    def get_memory_info(self) -> Dict[str, str]:
        """
        Function to monitor memory rss and vms.
        """
        mem_info = self.process_info.memory_info()._asdict()
        mem_rss = self.convert_bytes(
            data = mem_info.get("rss"), unit = self.unit
        )
        mem_vms = self.convert_bytes(
            data = mem_info.get("vms"), unit = self.unit
        )
        return {"memory_rss": mem_rss, "memory_vms": mem_vms}

    def get_folder_size(self) -> Dict[str, float]:
        """
        Function to get folder size.
        """

        path = self.config.get('folder_path')

        if not os.path.exists(path):
            raise FileNotFoundError(f"folder_path: {folder_path} not found.")

        folder_size, folder_path = sh.du("-s", path).splitlines()[0].split('\t')
        folder_size = self.convert_bytes(
            data = folder_size, unit = self.unit
        )
        
        return {"folder_size":folder_size, "folder_path": folder_path}

    def convert_bytes(self, data: Union[str, int, float], unit: str) -> float:
        """
        Convert data to input unit.
        """
        custom_format = lambda target: float(f"{target:.2f}")
        
        to_B  = lambda x: float(x)
        to_KB = lambda x: to_B(x)/1024
        to_MB = lambda x: to_KB(x)/1024
        to_GB = lambda x: to_MB(x)/1024
        to_TB = lambda x: to_GB(x)/1024

        converters = {
            "B" : to_B , "KB": to_KB,
            "MB": to_MB, "GB": to_GB,
            "TB": to_TB
        }
        
        converter = converters.get(unit)
        if converter == None:
            logger.warning(f"{unit} conversion not defined, convert data to B")
            return custom_format(to_B(data))
        else:
            return custom_format(converter(data))
