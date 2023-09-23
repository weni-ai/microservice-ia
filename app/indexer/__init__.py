from abc import ABC, abstractmethod

class IDocumentIndexer(ABC):
    @abstractmethod
    def index(self):
        pass
    
    @abstractmethod
    def index_batch(self):
        pass
    
    @abstractmethod
    def search(self):
        pass
    
    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def delete_batch(self):
        pass
