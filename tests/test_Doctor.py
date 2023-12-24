import pytest
from src.Doctor import porcess_decartor
import time

@porcess_decartor("./tests/test-config/monitor_prometheus.json")
def test_process_decator():
    
    total: int = 0

    t1 = time.time()
    while True:
        total += 1
        if time.time() - t1 > 30:
            break
