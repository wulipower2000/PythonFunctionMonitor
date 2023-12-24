import os
import threading

from Exporter import ProcessExporter
from typing import Callable

def porcess_decartor(config_path: str) -> Callable:

    def decorator(func: Callable) -> Callable:
        
        def wrapper(*args, **kwargs):

            pid = os.getpid()
            process_exporter = ProcessExporter(
                pid = pid,
                config_path = config_path,
                func_name = func.__name__
            )
            daemon = threading.Thread(
                target = process_exporter.start, daemon=True
            )
            daemon.start()
            
            result = func(*args, **kwargs)
            
            process_exporter.stop()
            daemon.join()

            return result
        return wrapper
    return decorator
