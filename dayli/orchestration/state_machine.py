from dataclasses import dataclass


@dataclass(slots=True)
class WorkflowState:
    current_step: str = "planner"

