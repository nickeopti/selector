import pytest

import selector


def test_required_args_missing_get_argument():
    with pytest.raises(SystemExit):
        selector.get_argument('value', int, args=())


def test_required_args_missing_add_arguments():
    def f(value: int):
        return value

    with pytest.raises(SystemExit):
        selector.add_arguments('f', f, args=())
