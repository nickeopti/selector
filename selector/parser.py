from argparse import ArgumentParser


class Parser:
    def __init__(self) -> None:
        self._parser: ArgumentParser | None = None

    def get(self) -> ArgumentParser:
        if self._parser is None:
            self._parser = ArgumentParser(allow_abbrev=False, add_help=False)
        return self._parser

    def set(self, parser: ArgumentParser) -> None:
        self._parser = parser

    def reset(self) -> None:
        self._parser = None


parser = Parser()
