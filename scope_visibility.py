"""Conservative Squirrel lexical visibility checks for dragged local symbols.

This is an editor-side safety guard, not a complete Squirrel name resolver.
"""
from __future__ import annotations


def _locations(section):
    found = {}
    def visit(items, containers, ancestors):
        for index, block in enumerate(items):
            found[block.id] = (block, containers, ancestors, index, items)
            for name, children in block.branches.items():
                visit(children, containers + ((block.id, name),), ancestors + ((block.id, index),))
    visit(section.blocks, (), ())
    return found


def visible_local(section, source_id, destination_id):
    """Whether an identified local variable/parameter can be referenced at destination.

    Event `env` is a parameter of that event's body. Variables declared in a
    C-shaped branch are not accessible outside that branch. A local declaration
    must also precede its use in the surrounding statement list.
    """
    locations = _locations(section)
    if source_id not in locations or destination_id not in locations:
        return False
    source, source_path, _, src_index, src_list = locations[source_id]
    dest, dest_path, dest_ancestors, dest_index, dest_list = locations[destination_id]
    if source.kind == 'event':
        needed_path = source_path + ((source.id, 'body'),)
    else:
        needed_path = source_path
    if dest_path[:len(needed_path)] != needed_path:
        return False
    if source.kind == 'event':
        return True
    if dest_list is src_list:
        return src_index < dest_index or source_id == destination_id
    # A destination nested inside a later/equal enclosing statement can see
    # the declaration; an earlier enclosing statement cannot.
    if len(dest_ancestors)>len(source_path):
        enclosing_block_id, enclosing_index = dest_ancestors[len(source_path)]
        return enclosing_index > src_index
    return False


def resolve_socket_statement(owner):
    """Find the real source statement behind any depth of embedded expressions.

    Nested expression adapters have ``outer`` rather than ``section``.
    Lexical visibility must use the enclosing statement, not an embedded AST id.
    """
    visited=set()
    while hasattr(owner, 'outer'):
        if id(owner) in visited:
            return None, None
        visited.add(id(owner))
        owner=owner.outer
    section=getattr(owner, 'root_section', None)
    block=getattr(owner, 'block', None)
    return section, getattr(block, 'id', None)
