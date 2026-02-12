from argparse import ArgumentParser

import pytest

import selector


@pytest.mark.parametrize("value", ["true", "True", "TRUE", "false", "False", "FALSE"])
def test_bool_converter(value):
    parser = ArgumentParser()
    
    def f(value: bool):
        return value
    
    g = selector.add_arguments(parser, "f", f, args=('--value', value))

    v = g()
    assert isinstance(v, bool)
    assert v == (value.lower() == "true")
