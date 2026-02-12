from typing import Any, Callable, TypeVar

T = TypeVar('T')


class Converter:
    def __init__(self) -> None:
        self.converters: dict[type, Callable[[str], Any]] = {}

    def add(self, type: type[T], converter: Callable[[str], T]) -> None:
        self.converters[type] = converter

    def get(self, type: type[T]) -> Callable[[str], T]:
        return self.converters.get(type, type)


converter = Converter()


def to_bool(value: str) -> bool:
    match value.lower():
        case 'true':
            return True
        case 'false':
            return False
        case _:
            raise ValueError(f'Invalid bool value: {value!r}')


converter.add(bool, to_bool)
