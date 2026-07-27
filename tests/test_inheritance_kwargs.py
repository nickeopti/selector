from typing import Any

import selector
from selector.arguments import _get_arguments, _takes_kwargs  # type: ignore


class _Base:
    def __init__(self, a: int) -> None:
        self.a = a


class _MiddleWithKwargs(_Base):
    def __init__(self, b: int, **kwargs: Any) -> None:
        self.b = b
        super().__init__(**kwargs)


class _ChildWithKwargs(_MiddleWithKwargs):
    def __init__(self, c: int, **kwargs: Any) -> None:
        self.c = c
        super().__init__(**kwargs)


class _LeafWithoutKwargs(_Base):
    def __init__(self, x: int) -> None:
        self.x = x
        super().__init__(a=0)


class _MiddleWithoutKwargs(_Base):
    def __init__(self, b: int) -> None:
        self.b = b
        super().__init__(a=0)


class _ChildAboveNonForwardingMiddle(_MiddleWithoutKwargs):
    def __init__(self, c: int, **kwargs: Any) -> None:
        self.c = c
        super().__init__(**kwargs)


class _WithRenamedVarKeyword:
    def __init__(self, x: int, **options: Any) -> None:
        self.x = x


def _argument_names(cls: type[object]) -> set[str]:
    return {parameter.name for parameter in _get_arguments(cls)}


def test_takes_kwargs_detects_var_keyword() -> None:
    assert _takes_kwargs(_WithRenamedVarKeyword.__init__) is True


def test_takes_kwargs_rejects_keyword_only_params() -> None:
    class WithKeywordOnly:
        def __init__(self, x: int, *, y: int = 1) -> None:
            self.x = x

    assert _takes_kwargs(WithKeywordOnly.__init__) is False


def test_get_arguments_collects_along_kwargs_forwarding_chain() -> None:
    assert _argument_names(_ChildWithKwargs) == {'a', 'b', 'c'}


def test_get_arguments_stops_at_class_without_var_keyword() -> None:
    assert _argument_names(_LeafWithoutKwargs) == {'x'}


def test_get_arguments_does_not_collect_past_non_forwarding_middle() -> None:
    assert _argument_names(_ChildAboveNonForwardingMiddle) == {'b', 'c'}


def test_subclass_parameters_take_precedence_on_name_clash() -> None:
    class Base:
        def __init__(self, shared: int) -> None:
            self.base_shared = shared

    class Child(Base):
        def __init__(self, shared: int, **kwargs: Any) -> None:
            super().__init__(**kwargs)

    parameters = _get_arguments(Child)
    shared_parameters = [parameter for parameter in parameters if parameter.name == 'shared']

    assert len(shared_parameters) == 1
    assert shared_parameters[0].annotation is int


def test_add_arguments_instantiates_along_kwargs_forwarding_chain() -> None:
    instance = selector.add_arguments(
        'child',
        _ChildWithKwargs,
        args=('--c', '1', '--b', '2', '--a', '3'),
    )()

    assert isinstance(instance, _ChildWithKwargs)
    assert instance.c == 1
    assert instance.b == 2
    assert instance.a == 3


def test_add_arguments_instantiates_leaf_without_var_keyword() -> None:
    instance = selector.add_arguments('leaf', _LeafWithoutKwargs, args=('--x', '7'))()

    assert isinstance(instance, _LeafWithoutKwargs)
    assert instance.x == 7
