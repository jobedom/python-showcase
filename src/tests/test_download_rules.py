import time

from pytest import fixture

from download_rules import DownloadRules

MAX_FILE_COUNT = 2
LIMIT_SIZE_BYTES = 1000
LIMIT_TIME_SECS = 0.25
TEST_IP = "127.0.0.1"


@fixture
def download_rules():
    return DownloadRules(MAX_FILE_COUNT, LIMIT_SIZE_BYTES, LIMIT_TIME_SECS)


def test_has_file_count_reached_limit(download_rules):
    assert not download_rules.has_file_count_reached_limit(0)
    assert not download_rules.has_file_count_reached_limit(MAX_FILE_COUNT - 1)
    assert download_rules.has_file_count_reached_limit(MAX_FILE_COUNT)
    assert download_rules.has_file_count_reached_limit(MAX_FILE_COUNT + 1)


def test_ip_over_download_rate_limit(download_rules):
    assert not download_rules.is_ip_over_download_rate_limit(TEST_IP)
    download_rules.register_download(TEST_IP, LIMIT_SIZE_BYTES)
    download_rules.register_download(TEST_IP, LIMIT_SIZE_BYTES)
    download_rules.register_download(TEST_IP, LIMIT_SIZE_BYTES)
    assert download_rules.is_ip_over_download_rate_limit(TEST_IP)
    time.sleep(LIMIT_TIME_SECS * 1.5)
    assert not download_rules.is_ip_over_download_rate_limit(TEST_IP)
