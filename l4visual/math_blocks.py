"""Squirrel math-library metadata and safe expression builders."""
OPERATORS={
 '算术':('+','-','*','/','%'),
 '比较':('>','<','>=','<=','==','!='),
 '逻辑':('&&','||','!'),
 '位运算':('&','|','^','<<','>>')
}
OPERATOR_SET={item for group in OPERATORS.values() for item in group}
MATH_FUNCTIONS={
 'abs':1,'acos':1,'asin':1,'atan':1,'atan2':2,'ceil':1,'cos':1,
 'exp':1,'fabs':1,'floor':1,'log':1,'log10':1,'pow':2,
 'sin':1,'sqrt':1,'tan':1,
 'max':2,'min':2
}

# max/min are editor-provided named Squirrel helpers, not assumed engine globals.
CUSTOM_MATH_HELPERS={'max':'Max','min':'Min'}
# L4D2 standard builds may expose subsets of optional math functions.
# Only registered built-ins should be placed in this list; custom APIs belong elsewhere.
def emit_operator(args,expression):
    op=str(args.get('operator','+'))
    if op not in OPERATOR_SET:raise ValueError('无效运算符 '+op)
    if op=='!':return '(!'+expression(args.get('left','false'))+')'
    return '('+expression(args.get('left','0'))+' '+op+' '+expression(args.get('right','0'))+')'

def emit_math(args,expression):
    name=str(args.get('function','sqrt'))
    if name not in MATH_FUNCTIONS:raise ValueError('未登记的数学函数 '+name)
    params=list(args.get('parameters',[]))
    if len(params)!=MATH_FUNCTIONS[name]:raise ValueError(name+' 参数数量应为 '+str(MATH_FUNCTIONS[name]))
    target='::L4VP_Utils.'+CUSTOM_MATH_HELPERS[name] if name in CUSTOM_MATH_HELPERS else name
    return target+'('+', '.join(expression(a) for a in params)+')'
