from argparse import ArgumentParser
from typing import Optional

import selector


def test_args():
    parser = ArgumentParser()
    
    def f(value: int):
        return value
    
    g = selector.add_arguments(parser, "f", f, args=('--value', '1'))
    
    assert g() == 1

def test_optional_args():
    parser = ArgumentParser()
    
    def f(value: int | None = None):
        return value
    
    g = selector.add_arguments(parser, "f", f, args=('--value', '1'))

    assert g() == 1


def test_optional_args_old_style():
    parser = ArgumentParser()
    
    def f(value: Optional[int] = None):
        return value
    
    g = selector.add_arguments(parser, "f", f, args=('--value', '1'))

    assert g() == 1
