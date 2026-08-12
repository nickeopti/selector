import pytest

import selector


def test_valid_choice():
    v = selector.get_argument('mode', str, choices=['train', 'eval'], args=('--mode', 'train'))

    assert v == 'train'


def test_invalid_choice():
    with pytest.raises(SystemExit):
        selector.get_argument('mode', str, choices=['train', 'eval'], args=('--mode', 'invalid'))


def test_default_choice():
    v = selector.get_argument('mode', str, choices=['train', 'eval'], default='eval')

    assert v == 'eval'


def test_valid_choice_list():
    v = selector.get_argument('mode', list[str], choices=['train', 'eval'], args=('--mode', 'train', '--mode', 'eval'))

    assert v == ['train', 'eval']


def test_invalid_choice_list():
    with pytest.raises(SystemExit):
        selector.get_argument(
            'mode', list[str], choices=['train', 'eval'], args=('--mode', 'eval', '--mode', 'invalid')
        )


def test_default_choice_list():
    v = selector.get_argument('mode', list[str], choices=['train', 'eval'], default=['eval'])

    assert v == ['eval']
