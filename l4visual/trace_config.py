"""TraceLine statement / expression configuration model (does not depend on Qt)."""

TRACE_FIELDS = ('start', 'end', 'ignore', 'mask')
TRACE_DEFAULTS = ('Vector(0, 0, 0)', 'Vector(1000, 0, 0)', 'null', '33579137')


def current_trace_values(block):
    if block.kind == 'trace_line':
        return [block.args.get(k, v) for k, v in zip(TRACE_FIELDS, TRACE_DEFAULTS)]
    if block.kind == 'utility' and block.args.get('operation') == 'trace_ray':
        params = list(block.args.get('parameters', []))
        return [block.args.get('value', TRACE_DEFAULTS[0])] + [
            params[i] if i < len(params) else TRACE_DEFAULTS[i + 1] for i in range(3)]
    raise ValueError('Unsupported TraceLine block')


def update_trace_values(block, values):
    """Keep embedded expression AST values intact when dialog fields are unchanged."""
    if len(values) != 4:
        raise ValueError('TraceLine requires four expressions')
    if block.kind == 'trace_line':
        block.args.update(zip(TRACE_FIELDS, values))
    elif block.kind == 'utility' and block.args.get('operation') == 'trace_ray':
        block.args['value'] = values[0]
        block.args['parameters'] = list(values[1:])
    else:
        raise ValueError('Unsupported TraceLine block')
