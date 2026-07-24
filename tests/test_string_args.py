import selector


def test_string_args():
    def f(value: 'int'):
        return value

    g = selector.add_arguments('f', f, args=('--value', '1'))

    v = g()
    assert isinstance(v, int)
    assert v == 1
