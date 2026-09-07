from __future__ import annotations

import dataclasses
import enum
import inspect
import typing
import warnings
from argparse import ArgumentParser, SUPPRESS
from functools import partial
from types import ModuleType, UnionType
from typing import TYPE_CHECKING, Any, Callable, final, Literal, Sequence, Type, TypeVar, Union

if TYPE_CHECKING:
    from typing_extensions import TypeForm

from selector.converters import converter
from selector.parser import parser as default_parser
from selector.postprocessors import postprocessor

T = TypeVar('T')


@final
class Unset:
    def __repr__(self) -> str:
        return 'UNSET'


UNSET = Unset()


def get_argument(
    name: str,
    type: TypeForm[T],
    default: T | Unset = UNSET,
    choices: Sequence[T] | None = None,
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> T:
    argument_parser = _resolve_parser(parser)

    type_info = _unpack_type(type)
    match type_info:
        case Unsupported.TYPE_HINT_IS_ANY:
            raise ValueError(f'Type hint for {name!r} is Any which is unsupported')
        case Unsupported.TYPE_HINT_MISSING:
            raise ValueError(f'Type hint for {name!r} seems to be missing')
        case Unsupported.TYPE_HINT_MISSING_ITEM_TYPE:
            raise ValueError(f'Type hint for {name!r} missing type hint for collection items')
        case Unsupported.MULTIPLE_TYPES:
            raise ValueError(f'Type hint for {name!r} is multiple types which is unsupported, got {type!r}')
        case UnpackedTypeInfo():
            pass

    if name not in _previously_known_arguments(argument_parser):
        argument_parser.add_argument(
            f'--{name}',
            type=converter.get(type_info.type),
            default=default if default is not UNSET else None if type_info.is_optional else SUPPRESS,
            choices=choices or type_info.literal_values,
            action='append' if type_info.is_append_container else 'store',
            required=default is UNSET and not (type_info.is_optional or type_info.is_append_container),
        )

    parsed_args, _ = argument_parser.parse_known_args(args)
    if type_info.is_optional and (value := getattr(parsed_args, name)) is None:
        return value
    if type_info.is_append_container and name not in parsed_args:
        value = []
    else:
        value = getattr(parsed_args, name)
    return type_info.postprocessor(value)


def add_arguments(
    name: str,
    reference: Type[T] | Callable[..., T],
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> partial[T]:
    # TODO: Arguments not specified should be excluded, not set to None

    argument_parser = _resolve_parser(parser)
    argument_group = argument_parser.add_argument_group(name)

    argument_postprocessors: dict[str, Callable[[Any], Any]] = {}

    previously_known_arguments = _previously_known_arguments(argument_parser)
    arguments = (
        _get_arguments(reference) if isinstance(reference, type) else _get_function_arguments(reference).values()
    )
    for argument in arguments:
        type_hint = argument.annotation

        if isinstance(type_hint, str):
            try:
                type_hint = eval(type_hint)
            except Exception:
                warnings.warn(
                    f'Type hint for {argument.name!r} is not supported by selector, got {type_hint!r}, skipping'
                )
                continue

        type_info = _unpack_type(type_hint)
        match type_info:
            case Unsupported.TYPE_HINT_IS_ANY:
                warnings.warn(f'Type hint for {argument.name!r} is Any which is unsupported, skipping')
                continue
            case Unsupported.TYPE_HINT_MISSING:
                warnings.warn(f'Type hint for {argument.name!r} seems to be missing, skipping')
                continue
            case Unsupported.TYPE_HINT_MISSING_ITEM_TYPE:
                warnings.warn(f'Type hint for {argument.name!r} missing type hint for collection items, skipping')
                continue
            case Unsupported.MULTIPLE_TYPES:
                warnings.warn(
                    f'Type hint for {argument.name!r} is multiple types which is unsupported, got {type_hint!r}, skipping'
                )
                continue
            case UnpackedTypeInfo():
                pass

        argument_postprocessors[argument.name] = type_info.postprocessor

        if argument.name in previously_known_arguments:
            continue

        argument_group.add_argument(
            f'--{argument.name}',
            type=converter.get(type_info.type),
            action='append' if type_info.is_append_container else 'store',
            choices=type_info.literal_values,
        )

    temp_args, _ = argument_parser.parse_known_args(args)
    argument_values = {
        argument.name: argument_postprocessors[argument.name](vars(temp_args)[argument.name])
        for argument in arguments
        if argument.name in vars(temp_args) and vars(temp_args)[argument.name] is not None
    }

    return partial(reference, **argument_values)


def add_options(
    name: str,
    options: Sequence[Type[T]],
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> partial[T]:
    argument_parser = _resolve_parser(parser)
    argument_group = argument_parser.add_argument_group(name)

    argument_group.add_argument(
        f'--{name}',
        type=str,
        default=options[0].__name__,
        required=True,
    )
    temp_args, _ = argument_parser.parse_known_args(args)

    selected_class_name = vars(temp_args)[name]

    selectable_classes = {c.__name__: c for c in options}
    if selected_class_name not in selectable_classes:
        raise ValueError(f'Specified class name {selected_class_name!r} is not selectable (check for typos)')
    selected_class = selectable_classes[selected_class_name]

    return add_arguments(selected_class_name, selected_class, parser=argument_parser, args=args)


def add_options_from_module(
    name: str,
    module: ModuleType,
    of_subclass: Type[T],
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> partial[T]:
    argument_parser = _resolve_parser(parser)

    origin = typing.get_origin(of_subclass)
    proper_class_type = origin if origin is not None else of_subclass

    def predicate(obj: object) -> bool:
        return inspect.isclass(obj) and issubclass(obj, proper_class_type)

    valid_classes = inspect.getmembers(module, predicate)
    options = [valid_class for _, valid_class in valid_classes]

    return add_options(name, options, parser=argument_parser, args=args)


def _get_function_arguments(function: Callable[..., Any]) -> dict[str, inspect.Parameter]:
    signature = inspect.signature(function)

    parameters = {k: p for k, p in signature.parameters.items() if p.kind == p.POSITIONAL_OR_KEYWORD}

    return parameters


def _takes_kwargs(function: Callable[..., Any]) -> bool:
    signature = inspect.signature(function)
    return any(p.kind == p.VAR_KEYWORD for p in signature.parameters.values())


def _get_arguments(
    from_object: Type[object], excluded_parameters: Sequence[str] = ('self', 'cls', 'device')
) -> list[inspect.Parameter]:
    all_parameters: dict[str, inspect.Parameter] = {}

    for base in from_object.__mro__:
        parameters = _get_function_arguments(base.__init__)  # type: ignore
        all_parameters = parameters | all_parameters  # Let subclass parameters take precedence

        if not _takes_kwargs(base.__init__):
            break

    return [parameter for parameter in all_parameters.values() if parameter.name not in excluded_parameters]


def _previously_known_arguments(argument_parser: ArgumentParser) -> list[str]:
    return [argument.option_strings[0][2:] for argument in argument_parser._actions]


@dataclasses.dataclass(frozen=True)
class UnpackedTypeInfo[T]:
    type: type[T]
    is_optional: bool
    is_append_container: bool
    literal_values: tuple[T, ...] | None
    postprocessor: Callable[[Any], T]


class Unsupported(enum.Enum):
    TYPE_HINT_IS_ANY = enum.auto()
    TYPE_HINT_MISSING = enum.auto()
    TYPE_HINT_MISSING_ITEM_TYPE = enum.auto()
    MULTIPLE_TYPES = enum.auto()


def _unpack_type(type_hint: TypeForm[T]) -> UnpackedTypeInfo[T] | Unsupported:
    hint: Any = type_hint

    is_optional = _is_optional(hint)
    if is_optional:
        types = typing.get_args(hint)
        i = types.index(None.__class__)
        hint = types[(i + 1) % 2]

    origin = typing.get_origin(hint)

    if origin in (Union, UnionType):
        return Unsupported.MULTIPLE_TYPES

    if hint is inspect.Parameter.empty:
        return Unsupported.TYPE_HINT_MISSING

    # Not really a type, but worth guarding against
    if hint is Any:
        return Unsupported.TYPE_HINT_IS_ANY

    if origin is None and hint in (list, tuple, set):
        return Unsupported.TYPE_HINT_MISSING_ITEM_TYPE

    if origin is Literal:
        literal_values = typing.get_args(hint)
        literal_types: list[type] = [type(value) for value in literal_values]
        if not all(isinstance(value, literal_types[0]) for value in literal_values):
            return Unsupported.MULTIPLE_TYPES
        hint = literal_types[0]
    else:
        literal_values = None

    is_append_container = origin in (list, tuple, set)
    if is_append_container:
        item_types = typing.get_args(hint)
        if not item_types or item_types[0] in (Any, inspect.Parameter.empty):
            return Unsupported.TYPE_HINT_MISSING_ITEM_TYPE
        hint = item_types[0]

    argument_postprocessor = postprocessor.get(origin if origin is not None else hint)

    return UnpackedTypeInfo(
        type=hint,
        is_optional=is_optional,
        is_append_container=is_append_container,
        literal_values=literal_values,
        postprocessor=argument_postprocessor,
    )


def _is_optional(annotation: Any) -> bool:
    if not typing.get_origin(annotation) in (Union, UnionType):
        return False

    types = typing.get_args(annotation)

    if None.__class__ not in types:
        return False

    return len(types) == 2


def _resolve_parser(parser: ArgumentParser | None) -> ArgumentParser:
    return parser or default_parser.get()
