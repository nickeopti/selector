import selector


def test_duplicate_args_get_argument():
    a = selector.get_argument('a', int, args=('--a', '1'))
    b = selector.get_argument('a', int, args=('--a', '2'))

    assert a == 1
    assert b == 2


def test_duplicate_args_add_arguments():
    def f(value: int):
        return value

    def g(value: int):
        return value

    f_ = selector.add_arguments('f', f, args=('--value', '1'))
    g_ = selector.add_arguments('g', g, args=('--value', '2'))

    assert f_() == 1
    assert g_() == 2


def test_duplicate_args_combination():
    def f(value: int):
        return value

    f_ = selector.add_arguments('f', f, args=('--value', '1'))
    value = selector.get_argument('value', int, args=('--value', '2'))

    assert f_() == 1
    assert value == 2
