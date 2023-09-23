from abc import ABC, abstractmethod

class IStorage(ABC):
    @abstractmethod
    def save(self) -> list[str]:
        pass

    @abstractmethod
    def save_batch(self) -> list[str]:
        pass
    
    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def query_search(self):
        pass
    
    @abstractmethod
    def delete(self):
        pass
    
    