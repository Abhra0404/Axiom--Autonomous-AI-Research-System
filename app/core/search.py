from abc import ABC, abstractmethod

from app.models.schemas import Source


class SearchProvider(ABC):

    @abstractmethod
    def search(self, query: str) -> list[Source]:
        pass