"""Determine property-name parameter slots in documented NetProps methods."""
from __future__ import annotations
import json
import re

_NETPROP = re.compile(r"^(?:Get|Set|Has|GetProp|SetProp|HasProp|GetPropArray|SetPropArray)")

def is_netprop_method(block):
    if block.kind != 'method':
        return False
    a=block.args
    owner=str(a.get('owner',''))
    target=str(a.get('target',''))
    method=str(a.get('method',''))
    return (owner=='CNetPropManager' or owner=='NetProps' or target=='NetProps') and bool(re.match(r'^(GetProp|SetProp|HasProp)',method))

def property_parameter_index(block):
    if not is_netprop_method(block):
        return None
    specs=block.args.get('parameter_specs',[])
    for i, spec in enumerate(specs):
        name=str(spec.get('name','')).casefold() if isinstance(spec,dict) else ''
        if name in ('prop','propname','property','propertyname','key','field','prop_name','prop_name_or_path') or ('prop' in name and 'value' not in name):
            return i
    return 1 if len(block.args.get('parameters',[]))>=2 else None

def selected_property(block,index):
    params=block.args.get('parameters',[])
    if index>=len(params):return ''
    value=params[index]
    if isinstance(value,dict) and value.get('kind')=='literal':return str(value.get('value',''))
    if isinstance(value,str):
        try:
            x=json.loads(value)
            return x if isinstance(x,str) else ''
        except (ValueError,TypeError):return ''
    return ''

def set_selected_property(block,index,choice):
    params=block.args.setdefault('parameters',[])
    params[index]={'kind':'literal','value':choice['property']}
    block.args['netprop_class']=choice['table']
    block.args['netprop_selected_type']=choice.get('prop_type','Int')
    # Enforce the selected NetProp's documented element type and array-ness.
    # A Float getter cannot correctly read an integer property like m_iClip1.
    method=str(block.args.get('method',''))
    if method.startswith(('GetProp','SetProp')):
        mode='Get' if method.startswith('Get') else 'Set'
        typ=choice.get('prop_type','Int')
        variant=mode+'Prop'+typ+('Array' if choice.get('array') else '')
        from .official_docs import official_functions
        documented=official_functions().get('CNetPropManager.'+variant,{})
        if documented:
            block.args['method']=variant
            specs=documented.get('parameters',[])
            old=block.args['parameters']
            block.args['parameters']=old[:len(specs)]+['0']*max(0,len(specs)-len(old))
            block.args['parameter_specs']=specs
            block.args['return_type']=documented.get('returns',block.args.get('return_type'))


def repair_saved_netprop_selection(block):
    """Upgrade a legacy selected NetProp's getter to its actual documented type.

    Only acts when the project already carries an explicit selector class and
    typed selection; never infer a property type from an arbitrary method name.
    """
    if not is_netprop_method(block):return False
    category=block.args.get('netprop_class','')
    idx=property_parameter_index(block)
    if not category or idx is None:return False
    from .netprop_catalog import resolve_property, api_type
    prop=selected_property(block,idx)
    row=resolve_property(category,prop)
    if row is None:return False
    action='Get' if block.args.get('method','').startswith('Get') else 'Set'
    wanted=action+'Prop'+api_type(row)+('Array' if row['type']=='array' else '')
    if wanted==block.args.get('method') and prop==row['name']:
        return False
    set_selected_property(block,idx,{'table':category,'property':row['name'],
                                    'array':row['type']=='array','prop_type':api_type(row)})
    return True
