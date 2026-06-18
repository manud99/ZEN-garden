import logging
from abc import ABC, abstractmethod
from typing import Callable, cast

from .events import (
    ConstructModelEvent,
    Event,
    EventType,
    InitEvent,
    PostOptimizationEvent,
    PostProcessEvent,
)
from .postprocess.postprocess import Postprocess
from .utils import InputDataChecks, StringUtils

logger = logging.getLogger(__name__)


class Module(ABC):
    @abstractmethod
    def register_listeners(self) -> list[tuple[EventType, Callable[[Event], None]]]:
        pass


class BaseModule(Module):
    def register_listeners(self):
        return [
            (EventType.INIT, self.handle_init_event),
            (EventType.CONSTRUCT_MODEL, self.handle_construct_model_event),
            (EventType.POST_OPTIMIZATION, self.handle_post_optimization_event),
            (EventType.POST_PROCESS, self.handle_post_process_event),
        ]

    def handle_init_event(self, _event: Event):
        event: InitEvent = cast(InitEvent, _event)
        print("DummyModule received InitEvent")

        input_data_checks = InputDataChecks(
            config=event.config, optimization_setup=None
        )
        input_data_checks.check_dataset()
        input_data_checks.read_system_file(event.config)
        input_data_checks.check_technology_selections()
        input_data_checks.check_year_definitions()
        event.data_checks = input_data_checks

    def handle_construct_model_event(self, _event: Event):
        event: ConstructModelEvent = cast(ConstructModelEvent, _event)
        print("DummyModule received ConstructModelEvent")
        print("Input data:", event.config)
        print("Zen model:", event.zen_model)

        # Needs a complete rewrite. Here we would construct the optimization problem,
        # or parts of it, based on the input data and the zen model.

        # optimization_setup.construct_optimization_problem()

    def handle_post_process_event(self, _event: Event):
        event: PostProcessEvent = cast(PostProcessEvent, _event)
        print("DummyModule received PostProcessEvent")
        print("Input data:", event.config)
        print("Zen model:", event.zen_model)

        scenario_name, subfolder, param_map = StringUtils.generate_folder_path(
            config=event.config,
            scenario=event.scenario,
            scenario_dict=event.scenario_dict,
            steps_horizon=event.steps_horizon,
            step=event.step,
        )
        Postprocess(
            event.optimizer,
            scenarios=event.config.scenarios,
            subfolder=subfolder,
            model_name=event.model_name,
            param_map=param_map,
            scenario_name=scenario_name,
        )

    def handle_post_optimization_event(self, _event: Event):
        event: PostOptimizationEvent = cast(PostOptimizationEvent, _event)
        print("DummyModule received PostOptimizationEvent")

        # Example, how to move functionality to a module
        # optimization_setup won't exist in this form anymore
        # TODO: rewrite this part to fit the new structure

        if event.optimizer.optimality:
            return

        event.optimizer.write_IIS(event.scenario)
        logger.warning(f"Optimization: {event.zen_model.termination_condition}")
        event.should_break = True


class ScalingModule(Module):
    def register_listeners(self) -> list[tuple[EventType, Callable[[Event], None]]]:
        return [
            (EventType.CONSTRUCT_MODEL, self.handle_construct_model_event),
            (EventType.POST_OPTIMIZATION, self.handle_post_optimization_event),
        ]

    def handle_construct_model_event(self, _event: Event):
        event: ConstructModelEvent = cast(ConstructModelEvent, _event)
        print("ScalingModule received ConstructModelEvent")
        event.optimizer.prepare_scaling()

    def handle_post_optimization_event(self, _event: Event):
        event: PostOptimizationEvent = cast(PostOptimizationEvent, _event)
        print("ScalingModule received PostOptimizationEvent")

        event.optimizer.re_scale()
