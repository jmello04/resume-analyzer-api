from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple


class AnalysisRepositoryInterface(ABC):

    @abstractmethod
    def create(self, filename: str, resume_text: str, result: dict) -> Any:
        pass

    @abstractmethod
    def get_by_id(self, analysis_id: int) -> Optional[Any]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[Any], int]:
        pass
