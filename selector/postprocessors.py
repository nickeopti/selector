from typing import Any, Callable, TypeVar

T = TypeVar('T')


class Postprocessor:
    def __init__(self) -> None:
        self.postprocessors: dict[type, Callable[[Any], Any]] = {}

    def add(self, type: type[T], postprocessor: Callable[[T], T]) -> None:
        self.postprocessors[type] = postprocessor

    def get(self, type: type[T]) -> Callable[[T], T]:
        return self.postprocessors.get(type, lambda x: x)


postprocessor = Postprocessor()

postprocessor.add(list, list)
postprocessor.add(tuple, tuple)
postprocessor.add(set, set)
