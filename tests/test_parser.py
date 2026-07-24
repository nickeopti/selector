from argparse import ArgumentParser

import selector


def test_default_parser_is_shared():
    def f(value: int):
        return value

    def g(other: int):
        return other

    f_ = selector.add_arguments('f', f, args=('--value', '1', '--other', '2'))
    g_ = selector.add_arguments('g', g, args=('--value', '1', '--other', '2'))

    assert f_() == 1
    assert g_() == 2


def test_explicit_parser():
    parser = ArgumentParser()

    def f(value: int):
        return value

    g = selector.add_arguments('f', f, parser=parser, args=('--value', '1'))

    assert g() == 1


def test_set_parser():
    parser = ArgumentParser()
    selector.parser.set(parser)

    def f(value: int):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    assert g() == 1
