import enum

import pytest

import selector


class Color(enum.Enum):
    RED = 'red'
    GREEN = 'green'


class Priority(enum.IntEnum):
    LOW = 1
    HIGH = 10


class Mode(enum.StrEnum):
    TRAIN = 'train'
    EVAL = 'eval'


class Phase(enum.Enum):
    WARMUP = enum.auto()
    TRAIN = enum.auto()
    COOLDOWN = enum.auto()


class Code(enum.Enum):
    A = 10
    B = 20


def test_enum_by_value():
    def f(color: Color):
        return color

    result = selector.add_arguments('f', f, args=('--color', 'red'))()

    assert result is Color.RED


def test_enum_by_member_name():
    def f(color: Color):
        return color

    result = selector.add_arguments('f', f, args=('--color', 'RED'))()

    assert result is Color.RED


def test_int_enum_by_value():
    def f(priority: Priority):
        return priority

    result = selector.add_arguments('f', f, args=('--priority', '1'))()

    assert result is Priority.LOW


def test_int_enum_by_member_name():
    def f(priority: Priority):
        return priority

    result = selector.add_arguments('f', f, args=('--priority', 'LOW'))()

    assert result is Priority.LOW


def test_str_enum_by_value():
    def f(mode: Mode):
        return mode

    result = selector.add_arguments('f', f, args=('--mode', 'train'))()

    assert result is Mode.TRAIN


def test_str_enum_by_member_name():
    def f(mode: Mode):
        return mode

    result = selector.add_arguments('f', f, args=('--mode', 'TRAIN'))()

    assert result is Mode.TRAIN


def test_auto_enum_by_member_name():
    def f(phase: Phase):
        return phase

    result = selector.add_arguments('f', f, args=('--phase', 'WARMUP'))()

    assert result is Phase.WARMUP


def test_auto_enum_by_value():
    def f(phase: Phase):
        return phase

    result = selector.add_arguments('f', f, args=('--phase', str(Phase.WARMUP.value)))()

    assert result is Phase.WARMUP


def test_manual_int_enum_by_value():
    def f(code: Code):
        return code

    result = selector.add_arguments('f', f, args=('--code', '10'))()

    assert result is Code.A


def test_manual_int_enum_by_member_name():
    def f(code: Code):
        return code

    result = selector.add_arguments('f', f, args=('--code', 'A'))()

    assert result is Code.A


def test_optional_enum():
    def f(color: Color | None = None):
        return color

    assert selector.add_arguments('f', f)() is None
    assert selector.add_arguments('f', f, args=('--color', 'green'))() is Color.GREEN


def test_list_of_enums():
    def f(colors: list[Color]):
        return colors

    result = selector.add_arguments('f', f, args=('--colors', 'red', '--colors', 'green'))()

    assert result == [Color.RED, Color.GREEN]


def test_invalid_enum_value():
    def f(color: Color):
        return color

    with pytest.raises(SystemExit):
        selector.add_arguments('f', f, args=('--color', 'blue'))()
