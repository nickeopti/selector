import types
from argparse import ArgumentParser
from typing import Generic, TypeVar

import selector

T = TypeVar('T', bound=int)


def test_add_options_generics():
    class A(Generic[T]): ...

    class B(A[T]): ...

    class C(A[T]): ...

    parser = ArgumentParser()
    v = selector.add_options('v', [A[int], B[int], C[int]], parser=parser, args=('--v', 'A'))()
    assert isinstance(v, A)

    parser = ArgumentParser()
    v = selector.add_options('v', [A[int], B[int], C[int]], parser=parser, args=('--v', 'B'))()
    assert isinstance(v, B)

    parser = ArgumentParser()
    v = selector.add_options('v', [A[int], B[int], C[int]], parser=parser, args=('--v', 'C'))()
    assert isinstance(v, C)


def test_add_options_from_module_generics():
    class A(Generic[T]): ...

    class B(A[T]): ...

    class C(A[T]): ...

    module_name = 'test_module'
    test_module = types.ModuleType(module_name)
    setattr(test_module, 'A', A)
    setattr(test_module, 'B', B)
    setattr(test_module, 'C', C)

    parser = ArgumentParser()
    v = selector.add_options_from_module('v', test_module, A[int], parser=parser, args=('--v', 'A'))()
    assert isinstance(v, A)

    parser = ArgumentParser()
    v = selector.add_options_from_module('v', test_module, A[int], parser=parser, args=('--v', 'B'))()
    assert isinstance(v, B)

    parser = ArgumentParser()
    v = selector.add_options_from_module('v', test_module, A[int], parser=parser, args=('--v', 'C'))()
    assert isinstance(v, C)
