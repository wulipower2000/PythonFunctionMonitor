import pytest
from src.ConfigParser import JsonConfigParser

@pytest.mark.parametrize("path", ["./tests/test-config/monitor.json", "./tests/test-config/monitor_prometheus.json"])
def test_JsonConfigParser_load(path: str) -> None:
    
    json_config_parser = JsonConfigParser(path)
    json_config = json_config_parser.load()
    
    assert isinstance(json_config, dict)

@pytest.mark.parametrize("path", ["alidmoiqjdioqwjdoiajsoidjasoid"])
def test_JsonConfigParser_check(path: str) -> None:

    with pytest.raises(FileNotFoundError):
        json_config_parser = JsonConfigParser(path)
        json_config_parser.check()
