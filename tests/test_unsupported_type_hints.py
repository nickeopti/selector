from typing import Any

import pytest

import selector


def test_any_type_hint():
    def f(x: Any):
        return x

    with pytest.warns(UserWarning, match='is Any which is unsupported'):
        selector.add_arguments('f', f)


def test_missing_type_hint():
    def f(x):  # type: ignore
        return x  # type: ignore
    
    with pytest.warns(UserWarning, match='seems to be missing'):
        selector.add_arguments('f', f)  # type: ignore


def test_missing_item_type_hint():
    def f(x: list[Any]):  # type: ignore
        return x  # type: ignore
    
    with pytest.warns(UserWarning, match='missing type hint for collection items'):
        selector.add_arguments('f', f)  # type: ignore

    def g(x: list):  # type: ignore
        return x  # type: ignore

    with pytest.warns(UserWarning, match='missing type hint for collection items'):
        selector.add_arguments('g', g)  # type: ignore


def test_multiple_types():
    def f(x: int | str):
        return x

    with pytest.warns(UserWarning, match='is multiple types which is unsupported'):
        selector.add_arguments('f', f)
