from typing import Literal

import pytest

import selector


def test_default_get_argument():
    v = selector.get_argument('value', int, default=1)
    assert v == 1

    v = selector.get_argument('value', int, default=1, args=('--value', '2'))
    assert v == 2


def test_default_add_arguments():
    def f(value: int = 1):
        return value

    v = selector.add_arguments('f', f)()
    assert v == 1

    v = selector.add_arguments('f', f, args=('--value', '2'))()
    assert v == 2


def test_default_add_arguments_supplied():
    def f(value: int = 1):
        return value

    f_ = selector.add_arguments('f', f)
    assert f_.args == ()
    assert f_.keywords == {'value': 1}
    assert f_() == 1


def test_default_literal_get_argument():
    v = selector.get_argument('value', Literal[1, 2, 3], default=1)
    assert v == 1

    v = selector.get_argument('value', Literal[1, 2, 3], default=1, args=('--value', '2'))
    assert v == 2


def test_default_literal_add_arguments():
    def f(value: Literal[1, 2, 3] = 1):
        return value

    v = selector.add_arguments('f', f)()
    assert v == 1

    v = selector.add_arguments('f', f, args=('--value', '2'))()
    assert v == 2


def test_default_container_get_argument():
    with pytest.raises(ValueError):
        selector.get_argument('value', list[int], default=[1])

    with pytest.raises(ValueError):
        selector.get_argument('value', list[int], default=[1], args=('--value', '2'))


def test_default_container_add_arguments():
    def f(value: list[int] = [1]):
        return value

    v = selector.add_arguments('f', f)()
    assert v == [1]


def test_invalid_default_get_argument():
    with pytest.raises(ValueError):
        selector.get_argument('value', int, default='hi')

    with pytest.raises(ValueError):
        selector.get_argument('value', int, default=None)
    
    with pytest.raises(ValueError):
        selector.get_argument('value', Literal[1, 2, 3], default=4)
