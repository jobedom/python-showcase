import time
from collections import defaultdict


class DownloadRules:
    def __init__(self, max_file_count, limit_size_bytes, limit_time_secs):
        self.max_file_count = max_file_count
        self.limit_size_bytes = limit_size_bytes
        self.limit_time_secs = limit_time_secs
        self.recent_downloaded_sizes_by_ip = defaultdict(list)

    def has_file_count_reached_limit(self, file_count):
        return file_count >= self.max_file_count

    def is_ip_over_download_rate_limit(self, ip):
        self._remove_expired_downloads()
        total_downloaded_size_from_ip = sum(download["size"] for download in self.recent_downloaded_sizes_by_ip[ip])
        return total_downloaded_size_from_ip > self.limit_size_bytes

    def register_download(self, ip, size):
        self.recent_downloaded_sizes_by_ip[ip].append({"size": size, "timestamp": time.time()})

    def _remove_expired_downloads(self):
        now = time.time()
        for ip, recent_downloads_for_ip in self.recent_downloaded_sizes_by_ip.items():
            self.recent_downloaded_sizes_by_ip[ip] = [
                recent_download
                for recent_download in recent_downloads_for_ip
                if now - recent_download["timestamp"] <= self.limit_time_secs
            ]
