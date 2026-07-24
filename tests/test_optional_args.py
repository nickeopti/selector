from typing import Optional

import selector


def test_args():
    def f(value: int):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    assert g() == 1


def test_optional_args():
    def f(value: int | None = None):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    assert g() == 1

    h = selector.add_arguments('f', f)

    assert h() is None


def test_optional_args_old_style():
    def f(value: Optional[int] = None):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    assert g() == 1

    h = selector.add_arguments('f', f)

    assert h() is None
