from abc import ABC, abstractmethod

class IStorage(ABC):
    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def save_batch(self):
        pass
    
    @abstractmethod
    def search(self):
        pass

