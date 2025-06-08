import inspect
import typing
import warnings
from argparse import ArgumentParser, _StoreAction
from functools import partial
from types import ModuleType
from typing import Callable, Sequence, Type, TypeVar, Union

T = TypeVar('T')


def to_bool(val: str):
    match val.lower():
        case 'true':
            return True
        case 'false':
            return False
        case _:
            raise ValueError()


CONVERTER = {
    bool: to_bool,
}


def get_argument(
    argument_parser: ArgumentParser,
    name: str,
    type: Type[T],
    default: T | None = None,
    *,
    args: Sequence[str] | None = None,
) -> T:
    argument_parser.add_argument(f'--{name}', type=CONVERTER.get(type, type), default=default)
    args, _ = argument_parser.parse_known_args(args)
    return getattr(args, name)


def add_arguments(
    argument_parser: ArgumentParser, name: str, reference: Type[T] | Callable, *, args: Sequence[str] | None = None
) -> partial[T]:
    # TODO: Arguments not specified should be excluded, not set to None

    argument_group = argument_parser.add_argument_group(name)

    previously_known_arguments = [
        argument.option_strings[0][2:] for argument in argument_parser._actions if isinstance(argument, _StoreAction)
    ]
    arguments = (
        _get_arguments(reference) if isinstance(reference, type) else _get_function_arguments(reference).values()
    )
    for argument in arguments:
        if argument.name in previously_known_arguments:
            continue

        if is_optional(argument.annotation):
            type_hint = typing.get_args(argument.annotation)[0]
            if type_hint is inspect._empty:
                warnings.warn(f'Type hint for {argument.name!r} seems to be missing')

            is_list = hasattr(type_hint, '__origin__') and type_hint.__origin__ is list
            if is_list:
                if not hasattr(type_hint, '__args__') or type_hint.__args__[0] is inspect._empty:
                    warnings.warn(f'Type hint for {argument.name!r} missing type hint for list items')
                type_hint = type_hint.__args__[0]

            argument_group.add_argument(
                f'--{argument.name}',
                type=CONVERTER.get(type_hint, type_hint),
                action='append' if is_list else None,
            )
        else:
            type_hint = argument.annotation
            if type_hint is inspect._empty:
                warnings.warn(f'Type hint for {argument.name!r} seems to be missing')

            is_list = hasattr(type_hint, '__origin__') and type_hint.__origin__ is list
            if is_list:
                if not hasattr(type_hint, '__args__') or type_hint.__args__[0] is inspect._empty:
                    warnings.warn(f'Type hint for {argument.name!r} missing type hint for list items')
                type_hint = type_hint.__args__[0]

            argument_group.add_argument(
                f'--{argument.name}',
                type=CONVERTER.get(type_hint, type_hint),
                action='append' if is_list else None,
            )

    temp_args, _ = argument_parser.parse_known_args(args)
    argument_values = {
        argument.name: vars(temp_args)[argument.name]
        for argument in arguments
        if vars(temp_args)[argument.name] is not None
    }

    return partial(reference, **argument_values)


def add_options(
    argument_parser: ArgumentParser, name: str, options: Sequence[Type[T]], *, args: Sequence[str] | None = None
) -> partial[T]:
    argument_group = argument_parser.add_argument_group(name)

    argument_group.add_argument(
        f'--{name}',
        type=str,
        default=options[0].__name__ if options[0] is not None else None,
    )
    temp_args, _ = argument_parser.parse_known_args(args)

    selected_class_name = vars(temp_args)[name]

    selectable_classes = {c.__name__: c for c in options if c is not None}
    if selected_class_name not in selectable_classes:
        raise ValueError(f'Specified class name {selected_class_name!r} is not selectable (check for typos)')
    selected_class = selectable_classes[selected_class_name]

    return add_arguments(argument_parser, selected_class_name, selected_class, args=args)


def add_options_from_module(
    argument_parser: ArgumentParser,
    name: str,
    module: ModuleType,
    of_subclass: Type[T],
    *,
    args: Sequence[str] | None = None,
) -> partial[T]:
    def predicate(obj):
        return inspect.isclass(obj) and issubclass(obj, of_subclass)

    valid_classes = inspect.getmembers(module, predicate)
    options = [valid_class for _, valid_class in valid_classes]

    return add_options(argument_parser, name, options, args=args)


def _get_function_arguments(function: Callable):
    signature = inspect.signature(function)

    parameters = {k: p for k, p in signature.parameters.items() if p.kind == p.POSITIONAL_OR_KEYWORD}

    return parameters


def _get_arguments(from_object: Type[object], excluded_parameters=('self', 'cls', 'device')):
    all_parameters: dict[str, inspect.Parameter] = {}

    for base in from_object.__mro__:
        parameters = _get_function_arguments(base.__init__)  # type: ignore
        all_parameters = parameters | all_parameters  # Let subclass parameters take precedence

    return [parameter for parameter in all_parameters.values() if parameter.name not in excluded_parameters]


def is_optional(annotation):
    return typing.get_origin(annotation) is Union and None.__class__ in typing.get_args(annotation)
