import enum
import inspect
from typing import Any, Callable, TypeVar

T = TypeVar('T')


class Converter:
    def __init__(self) -> None:
        self.converters: dict[type, Callable[[str, type[Any]], Any]] = {}

    def add(self, type: type[T], converter: Callable[[str, type[T]], T]) -> None:
        self.converters[type] = converter

    def _lookup_converter(self, type: type[T]) -> Callable[[str, type[Any]], Any]:
        if type in self.converters:
            return self.converters[type]

        if inspect.isclass(type):
            for base in type.__mro__:
                if base in self.converters:
                    return self.converters[base]

        return lambda value, type: type(value)

    def get(self, type: type[T]) -> Callable[[str], T]:
        return lambda value: self._lookup_converter(type)(value, type)


converter = Converter()


def to_bool(value: str, _: type[bool]) -> bool:
    match value.lower():
        case 'true':
            return True
        case 'false':
            return False
        case _:
            raise ValueError(f'Invalid bool value: {value!r}')


def to_enum(value: str, enum_class: type[enum.Enum]) -> enum.Enum:
    if value in enum_class.__members__:
        return enum_class[value]

    for member in enum_class:
        if str(member.value) == value:
            return member

    try:
        return enum_class(int(value))
    except (ValueError, KeyError):
        pass

    raise ValueError(f'Invalid enum value {value!r} for enum {enum_class.__name__!r}')


converter.add(bool, to_bool)
converter.add(enum.Enum, to_enum)
