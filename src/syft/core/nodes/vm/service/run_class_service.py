from __future__ import annotations

from ...abstract.service import NodeService
from ....message import RunClassMethodMessage
from ..... import type_hints
from ....pointer.pointer import Pointer
from .....common import AbstractNode
from typing import List


class RunClassMethodService(NodeService):
    @staticmethod
    @type_hints
    def process(node: AbstractNode, msg: RunClassMethodMessage) -> None:
        self_possibly_pointer = msg._self
        args_with_pointers = msg.args
        # kwargs_with_pointers = msg.kwargs

        result_id_at_location = msg.id_at_location

        # Step 1: Replace Pointers with Objects in self, args, and kwargs
        # self_is_object = None
        args_with_objects = list()

        kwargs_with_objects = {}

        # Step 1a: set self_is_object to be the object self_possibly_pointer points to
        if issubclass(type(self_possibly_pointer), Pointer):
            self_is_object = node.store.get_object(
                self_possibly_pointer.id_at_location
            )
        else:
            self_is_object = self_possibly_pointer

        # Step 1b: replace arg pointers with objects the pointers point to
        for arg in args_with_pointers:
            if issubclass(type(arg), Pointer):
                args_with_objects.append(node.store.get_object(arg.id_at_location))
            else:
                args_with_objects.append(arg)

        # Step 1c: replace kwarg pointers with objects the pointers point to
        for name, kwarg in kwargs_with_objects.items():
            if issubclass(type(kwarg), Pointer):
                args_with_objects[name] = node.store.get_object(kwarg.id_at_location)
            else:
                args_with_objects[name] = kwarg

        # Step 2: Execute method
        result = node.frameworks(msg.path)(
            self_is_object, *args_with_objects, **kwargs_with_objects
        )

        # Step 3: Store result
        node.store.store_object(result_id_at_location, result)

        pass

    @staticmethod
    @type_hints
    def message_handler_types() -> List[type]:
        return [RunClassMethodMessage]