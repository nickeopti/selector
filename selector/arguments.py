import inspect
import typing
from argparse import ArgumentParser, _StoreAction
from functools import partial
from types import ModuleType
from typing import Sequence, Type, TypeVar, Union

T = TypeVar("T")


def get_argument(argument_parser: ArgumentParser, name: str, type: Type[T], default: T = None) -> T:
    argument_parser.add_argument(f'--{name}', type=type, default=default)
    args, _ = argument_parser.parse_known_args()
    return getattr(args, name)


def add_arguments(
    argument_parser: ArgumentParser, name: str, class_ref: Type[T]
) -> partial[T]:
    # TODO: Arguments not specified should be excluded, not set to None

    argument_group = argument_parser.add_argument_group(name)

    previously_known_arguments = [
        argument.option_strings[0][2:]
        for argument in argument_parser._actions
        if isinstance(argument, _StoreAction)
    ]
    arguments = _get_arguments(class_ref)
    for argument in arguments:
        if argument.name in previously_known_arguments:
            continue

        if is_optional(argument.annotation):
            type_hint = typing.get_args(argument.annotation)[0]
            if type_hint is inspect._empty:
                raise ValueError(f'Type hint for {argument.name!r} seems to be missing')
            argument_group.add_argument(
                f"--{argument.name}",
                type=typing.get_args(argument.annotation)[0],
            )
        else:
            type_hint = argument.annotation
            if type_hint is inspect._empty:
                raise ValueError(f'Type hint for {argument.name!r} seems to be missing')
            argument_group.add_argument(
                f"--{argument.name}",
                type=argument.annotation,
            )

    temp_args, _ = argument_parser.parse_known_args()
    argument_values = {
        argument.name: vars(temp_args)[argument.name]
        for argument in arguments
        if vars(temp_args)[argument.name] is not None
    }

    return partial(class_ref, **argument_values)


def add_options(
    argument_parser: ArgumentParser, name: str, options: Sequence[Type[T]]
) -> partial[T]:
    argument_group = argument_parser.add_argument_group(name)

    argument_group.add_argument(
        f"--{name}",
        type=str,
        default=options[0].__name__ if options[0] is not None else None,
    )
    temp_args, _ = argument_parser.parse_known_args()

    selected_class_name = vars(temp_args)[name]

    selected_class = {c.__name__: c for c in options if c is not None}[
        selected_class_name
    ]

    return add_arguments(argument_parser, selected_class_name, selected_class)


def add_options_from_module(
    argument_parser: ArgumentParser,
    name: str,
    module: ModuleType,
    of_subclass: Type[T],
) -> partial[T]:
    def predicate(obj):
        return inspect.isclass(obj) and issubclass(obj, of_subclass)

    valid_classes = inspect.getmembers(module, predicate)
    options = [valid_class for _, valid_class in valid_classes]

    return add_options(argument_parser, name, options)


def _get_arguments(
    from_object: Type[object], excluded_parameters=("self", "cls", "device")
):
    all_parameters = {}

    for base in from_object.__mro__:
        signature = inspect.signature(base.__init__)
        parameters = {
            k: p
            for k, p in signature.parameters.items()
            if p.kind == p.POSITIONAL_OR_KEYWORD
        }
        all_parameters.update(parameters)

    return [
        parameter
        for parameter in all_parameters.values()
        if parameter.name not in excluded_parameters
    ]


def is_optional(annotation):
    return (
        typing.get_origin(annotation) is Union
        and None.__class__ in typing.get_args(annotation)
    )
