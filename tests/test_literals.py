from typing import Literal

import pytest

import selector


def test_literal_get_argument():
    v = selector.get_argument('mode', Literal['train', 'eval'], args=('--mode', 'train'))

    assert v == 'train'


def test_literal_add_arguments():
    def f(mode: Literal['train', 'eval']):
        return mode

    v = selector.add_arguments('f', f, args=('--mode', 'eval'))()

    assert v == 'eval'


def test_invalid_literal_get_argument():
    with pytest.raises(SystemExit):
        selector.get_argument('mode', Literal['train', 'eval'], args=('--mode', 'invalid'))


def test_invalid_literal_add_arguments():
    def f(mode: Literal['train', 'eval']):
        return mode

    with pytest.raises(SystemExit):
        selector.add_arguments('f', f, args=('--mode', 'invalid'))()


def test_optional_literal_get_argument():
    def f(mode: Literal['train', 'eval'] | None = None):
        return mode

    assert selector.add_arguments('f', f)() is None
    assert selector.add_arguments('f', f, args=('--mode', 'train'))() == 'train'


def test_optional_literal_add_arguments():
    def f(mode: Literal['train', 'eval'] | None = None):
        return mode

    assert selector.add_arguments('f', f)() is None
    assert selector.add_arguments('f', f, args=('--mode', 'train'))() == 'train'


def test_int_literal_get_argument():
    v = selector.get_argument('n', Literal[1, 2, 3], args=('--n', '2'))

    assert v == 2


def test_int_literal_add_arguments():
    def f(n: Literal[1, 2, 3]):
        return n

    v = selector.add_arguments('f', f, args=('--n', '2'))()

    assert v == 2
