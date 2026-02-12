from argparse import ArgumentParser

import selector


def test_duplicate_args_get_argument():
    parser = ArgumentParser()

    a = selector.get_argument(parser, "a", int, args=('--a', '1'))
    b = selector.get_argument(parser, "a", int, args=('--a', '2'))

    assert a == 1
    assert b == 2


def test_duplicate_args_add_arguments():
    parser = ArgumentParser()

    def f(value: int):
        return value

    def g(value: int):
        return value

    f_ = selector.add_arguments(parser, "f", f, args=('--value', '1'))
    g_ = selector.add_arguments(parser, "g", g, args=('--value', '2'))

    assert f_() == 1
    assert g_() == 2


def test_duplicate_args_combination():
    parser = ArgumentParser()

    def f(value: int):
        return value

    f_ = selector.add_arguments(parser, "f", f, args=('--value', '1'))
    value = selector.get_argument(parser, "value", int, args=('--value', '2'))

    assert f_() == 1
    assert value == 2
