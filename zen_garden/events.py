import logging
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from zen_garden.utils import InputDataChecks
from zen_garden.zen_model import ZenModel

from .default_config import Config

logger = logging.getLogger(__name__)


class EventType(Enum):
    INIT = 0
    CONSTRUCT_MODEL = 10
    POST_OPTIMIZATION = 20
    POST_PROCESS = 30


class Event(ABC):  # noqa: B024
    type: EventType = NotImplemented


class BreakableEvent(Event):
    should_break: bool = False


@dataclass
class InitEvent(Event):
    config: Config
    data_checks: Optional[InputDataChecks] = None
    type: EventType = EventType.INIT


@dataclass
class ConstructModelEvent(Event):
    config: Config
    zen_model: ZenModel
    optimizer: Any
    step: int
    type: EventType = EventType.CONSTRUCT_MODEL


@dataclass
class PostOptimizationEvent(BreakableEvent):
    zen_model: ZenModel
    optimizer: Any
    step: int
    scenario: str
    should_break: bool = False
    type: EventType = EventType.POST_OPTIMIZATION


@dataclass
class PostProcessEvent(Event):
    config: Config
    zen_model: ZenModel
    optimizer: Any
    scenario: str
    scenario_dict: dict
    steps_horizon: list[int]
    model_name: str
    step: int
    type: EventType = EventType.POST_PROCESS
