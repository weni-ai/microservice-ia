from abc import ABC, abstractmethod


class IFileDownloader(ABC):
    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def download_file(self):
        pass

    @abstractmethod
    def download_file_batch(self):
        pass

    @abstractmethod
    def download_file_bulk(self):
        pass
