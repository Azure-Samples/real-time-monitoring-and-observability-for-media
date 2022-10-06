import pytest


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("KUSTO_DATABASE", "fakeDB")
    monkeypatch.setenv("KUSTO_URI", "https://fakedataexplorer.region.kusto.windows.net")
    monkeypatch.setenv("SLOW_START_TABLE", "slow_start_data_anomaly")
    monkeypatch.setenv("STALL_BUFFERING_TABLE", "stall_buff_anomaly")
    monkeypatch.setenv("LOW_QUALITY_TABLE", "low_quality_anomaly")
    monkeypatch.setenv("MANAGED_CLIENT_ID", "xxx-123-234s")
