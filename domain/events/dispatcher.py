from collections import defaultdict
from typing import Callable, Any

class EventDispatcher:
    def __init__(self):
        self._handlers = defaultdict(list)

    def register(self, event_type: type, handler: Callable):
        self._handlers[event_type].append(handler)

    def dispatch(self, event: Any):
        event_type = type(event)
        for handler in self._handlers[event_type]:
            handler(event)

dispatcher = EventDispatcher()
