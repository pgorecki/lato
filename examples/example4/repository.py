from typing import Any, Optional, Protocol


class Repository(Protocol):
    def add(self, entity: Any):
        ...

    def get_all(self, predicate) -> list[Any]:
        ...

    def find_by_id(self, entity_id) -> Any:
        ...

    def find_one(self, predicate) -> Any:
        ...

    def delete(self, entity_id):
        ...


class InMemoryRepository(Repository):
    def __init__(self):
        self.entities = []

    def add(self, entity: Any):
        self.entities.append(entity)

    def get_all(self, predicate) -> list[Any]:
        return [entity for entity in self.entities if predicate(entity)]

    def find_by_id(self, entity_id) -> Optional[Any]:
        return next(entity for entity in self.entities if entity.id == entity_id)

    def find_by(self, predicate):
        return next(entity for entity in self.entities if predicate(entity))

    def delete(self, entity_id):
        self.entities = [entity for entity in self.entities if entity.id != entity_id]
