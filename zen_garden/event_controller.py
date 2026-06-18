from collections import defaultdict
from typing import Callable

from .events import BreakableEvent, Event, EventType
from .modules import Module


class EventController:
    _listeners: defaultdict[EventType, list[Callable[[Event], None]]] = defaultdict(
        list
    )
    _modules: list[Module] = []

    def register_module(self, module: type[Module]):
        instance = module()
        for type, callback in instance.register_listeners():
            self.register_listener(type, callback)

    def register_listener(
        self, event_type: EventType, listener: Callable[[Event], None]
    ):
        self._listeners[event_type].append(listener)

    def dispatch_event(self, event: Event):
        if len(self._listeners[event.type]) == 0:
            return

        for listener in self._listeners[event.type]:
            listener(event)
            if isinstance(event, BreakableEvent) and event.should_break:
                break
