import math

from lllc import ast as vy_ast
from lllc.semantics.types.bases import StorageSlot


def set_data_positions(vyper_module: vy_ast.Module) -> None:
    """
    Parse the annotated Vyper AST, determine data positions for all variables,
    and annotate the AST nodes with the position data.

    Arguments
    ---------
    vyper_module : vy_ast.Module
        Top-level Vyper AST node that has already been annotated with type data.
    """
    set_storage_slots(vyper_module)


def set_storage_slots(vyper_module: vy_ast.Module) -> None:
    """
    Parse module-level Vyper AST to calculate the layout of storage variables.
    """
    # Allocate storage slots from 0
    # note storage is word-addressable, not byte-addressable
    storage_slot = 0

    for node in vyper_module.get_children(vy_ast.FunctionDef):
        type_ = node._metadata["type"]
        if type_.nonreentrant is not None:
            type_.set_reentrancy_key_position(StorageSlot(storage_slot))
            # TODO use one byte - or bit - per reentrancy key
            # requires either an extra SLOAD or caching the value of the
            # location in memory at entrance
            storage_slot += 1

    for node in vyper_module.get_children(vy_ast.AnnAssign):
        type_ = node.target._metadata["type"]
        type_.set_position(StorageSlot(storage_slot))
        # CMC 2021-07-23 note that HashMaps get assigned a slot here.
        # I'm not sure if it's safe to avoid allocating that slot
        # for HashMaps because downstream code might use the slot
        # ID as a salt.
        storage_slot += math.ceil(type_.size_in_bytes / 32)


def set_calldata_offsets(fn_node: vy_ast.FunctionDef) -> None:
    pass


def set_memory_offsets(fn_node: vy_ast.FunctionDef) -> None:
    pass
