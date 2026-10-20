import selector


def test_default_int_promoted_to_float_get_argument():
    v = selector.get_argument('value', float, default=1, args=('--value', '1'))
    assert v == 1.0
    assert isinstance(v, float)

    v = selector.get_argument('value', float, default=1, args=())
    assert v == 1.0
    assert isinstance(v, float)


def test_default_int_promoted_to_float_add_arguments():
    def f(value: float = 1) -> float:
        return value

    v = selector.add_arguments('f', f, args=('--value', '1'))()
    assert v == 1.0
    assert isinstance(v, float)

    v = selector.add_arguments('f', f, args=())()
    assert v == 1.0
    assert isinstance(v, float)
