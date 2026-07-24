from argparse import ArgumentParser

import selector


def test_list_argument():
    parser = ArgumentParser()

    def f(xs: list[int]):
        return xs

    v = selector.add_arguments(parser, 'f', f, args=('--xs', '1', '--xs', '2', '--xs', '3'))()

    assert isinstance(v, list)
    assert v == [1, 2, 3]


def test_tuple_argument():
    parser = ArgumentParser()

    def f(xs: tuple[int, ...]):
        return xs

    v = selector.add_arguments(parser, 'f', f, args=('--xs', '1', '--xs', '2', '--xs', '3'))()

    assert isinstance(v, tuple)
    assert v == (1, 2, 3)


def test_set_argument():
    parser = ArgumentParser()

    def f(xs: set[int]):
        return xs

    v = selector.add_arguments(parser, 'f', f, args=('--xs', '1', '--xs', '2', '--xs', '3'))()

    assert isinstance(v, set)
    assert v == {1, 2, 3}
