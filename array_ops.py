"""L4D2 Squirrel 3 array methods: signatures and code generation.

The editor calls the UI container "Set", but the runtime type is array.
"""
from .models import Block

ARRAY_OPERATIONS = {
    'append': (['value'], 'void'),
    'push': (['value'], 'void'),
    'extend': (['array'], 'void'),
    'insert': (['index', 'value'], 'void'),
    'remove': (['index'], 'value'),
    'pop': ([], 'value'),
    'top': ([], 'value'),
    'resize': (['size', 'fill'], 'void'),
    'clear': ([], 'void'),
    'len': ([], 'int'),
    'reverse': ([], 'void'),
    'sort': ([], 'void'),
    'slice': (['start', 'end'], 'array'),
}


def new_array_operation(name='append', target='items'):
    if name not in ARRAY_OPERATIONS:
        raise ValueError('未知 Array 操作：' + name)
    slots, returns = ARRAY_OPERATIONS[name]
    return Block('array_op', {'target': target, 'operation': name,
                               'parameters': ['null' for _ in slots],
                               'parameter_specs': [{'name': s, 'type': 'unknown'} for s in slots],
                               'return_type': returns, 'output': ''})


def change_array_operation(block, operation):
    if operation not in ARRAY_OPERATIONS:
        raise ValueError('未知 Array 操作：' + operation)
    slots, returns = ARRAY_OPERATIONS[operation]
    previous = block.args.get('parameters', [])
    block.args['operation'] = operation
    block.args['parameters'] = [previous[i] if i < len(previous) else 'null' for i in range(len(slots))]
    block.args['parameter_specs'] = [{'name': s, 'type': 'unknown'} for s in slots]
    block.args['return_type'] = returns
    if returns == 'void':
        block.args['output'] = ''


def array_call(block, render):
    op = str(block.args.get('operation', 'append'))
    if op not in ARRAY_OPERATIONS:
        raise ValueError('未知 Array 操作：' + op)
    args = block.args.get('parameters', [])
    sizes = {'resize': (1,2), 'slice':(1,2)}
    low, high = sizes.get(op, (len(ARRAY_OPERATIONS[op][0]),len(ARRAY_OPERATIONS[op][0])))
    if not low <= len(args) <= high:
        raise ValueError('Array 操作参数数量错误：' + op)
    args = list(args)
    if op in ('resize','slice') and len(args) > 1 and args[-1] in ('', None, 'null'):
        args.pop()
    return render(block.args.get('target', 'items')) + '.' + op + '(' + ', '.join(render(x) for x in args) + ')'
