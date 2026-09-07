from typing import Optional

import selector


def test_args_get_argument():
    v = selector.get_argument('value', int, args=('--value', '1'))
    assert v == 1


def test_args_add_arguments():
    def f(value: int):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    assert g() == 1


def test_optional_args_get_argument():
    v = selector.get_argument('value', int | None, args=('--value', '1'))
    assert v == 1

    v = selector.get_argument('value', int | None, args=())
    assert v is None


def test_optional_args_add_arguments():
    def f(value: int | None = None):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    assert g() == 1

    h = selector.add_arguments('f', f, args=())

    assert h() is None


def test_optional_args_old_style_add_arguments():
    def f(value: Optional[int] = None):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    assert g() == 1

    h = selector.add_arguments('f', f, args=())

    assert h() is None


def test_optional_container_get_argument():
    v = selector.get_argument('value', list[int] | None, args=('--value', '1', '--value', '2'))
    assert v == [1, 2]

    v = selector.get_argument('value', list[int] | None, args=('--value', '1'))
    assert v == [1]

    v = selector.get_argument('value', list[int] | None, args=())
    assert v is None


def test_optional_container_add_arguments():
    def f(value: list[int] | None = None):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1', '--value', '2'))
    assert g() == [1, 2]

    h = selector.add_arguments('f', f, args=('--value', '1'))
    assert h() == [1]
    
    i = selector.add_arguments('f', f, args=())
    assert i() is None
