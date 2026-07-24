import pytest

import selector


@pytest.fixture(autouse=True)
def reset_selector_parser():
    selector.parser.reset()
    yield
    selector.parser.reset()
