from collections import deque

from selector.postprocessors import postprocessor


class Containers:
    def __init__(self) -> None:
        self.containers: set[type] = set()

    def add(self, container: type) -> None:
        self.containers.add(container)
        postprocessor.add(container, container)

    def __contains__(self, container: type) -> bool:
        return container in self.containers


containers = Containers()

containers.add(list)
containers.add(tuple)
containers.add(set)
containers.add(frozenset)
containers.add(deque)
