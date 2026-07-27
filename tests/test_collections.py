import selector


def test_list_argument_get_argument():
    v = selector.get_argument('xs', list[int], args=('--xs', '1', '--xs', '2', '--xs', '3'))

    assert isinstance(v, list)
    assert v == [1, 2, 3]


def test_list_argument_add_arguments():
    def f(xs: list[int]):
        return xs

    v = selector.add_arguments('f', f, args=('--xs', '1', '--xs', '2', '--xs', '3'))()

    assert isinstance(v, list)
    assert v == [1, 2, 3]


def test_tuple_argument_get_argument():
    v = selector.get_argument('xs', tuple[int, ...], args=('--xs', '1', '--xs', '2', '--xs', '3'))

    assert isinstance(v, tuple)
    assert v == (1, 2, 3)


def test_tuple_argument_add_arguments():
    def f(xs: tuple[int, ...]):
        return xs

    v = selector.add_arguments('f', f, args=('--xs', '1', '--xs', '2', '--xs', '3'))()

    assert isinstance(v, tuple)
    assert v == (1, 2, 3)


def test_set_argument_get_argument():
    v = selector.get_argument('xs', set[int], args=('--xs', '1', '--xs', '2', '--xs', '3'))

    assert isinstance(v, set)
    assert v == {1, 2, 3}


def test_set_argument_add_arguments():
    def f(xs: set[int]):
        return xs

    v = selector.add_arguments('f', f, args=('--xs', '1', '--xs', '2', '--xs', '3'))()

    assert isinstance(v, set)
    assert v == {1, 2, 3}
