from typing import List
from typing import Union

import syft as sy

from syft.execution.role import Role
from syft.execution.role_assignments import RoleAssignments
from syft.exceptions import PlaceholderNotInstantiatedError

from syft.generic.abstract.sendable import AbstractSendable


class ProtocolExecution(AbstractSendable):
    """
    """

    def __init__(
        self,
        role: Role,
        role_assignments: RoleAssignments,
        # General kwargs
        id_: Union[str, int] = None,
        owner: "sy.workers.BaseWorker" = None,
        tags: List[str] = None,
        input_types: list = None,
        description: str = None,
    ):
        super().__init__(id_, owner, tags, description, child=None)

        # Template Role
        self.role = role
        # Placholders that will be instantiated during the execution
        self.placeholders = {}
        for ph_id, ph in role.placeholders.items():
            copy = ph.copy()
            copy.child = None
            copy.id = ph.id
            self.placeholders[ph_id] = copy
        # Needed to know with which workers we need to interact
        self.role_assignments = role_assignments

        # Index of the next action to execute
        self._next_action_index = 0

    def execute(self):
        for action in self.role.actions[self._next_action_index :]:
            try:
                self.role._execute_action(action)
                self._next_action_index += 1
            except PlaceholderNotInstantiatedError:
                return False, None

        if len(self.role.output_placeholder_ids) == 0:
            return True, None

        output_placeholders = [
            self.placeholders[output_id] for output_id in self.role.output_placeholder_ids
        ]

        return True, tuple(p.child for p in output_placeholders)
