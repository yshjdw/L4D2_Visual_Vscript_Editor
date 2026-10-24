"""User-facing UI descriptions. Never used by the Squirrel generator.

The code generator keeps canonical API/variable/event names; this module only
changes the widget text and the order of visual fields.
"""
from __future__ import annotations
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class DisplayProfile:
    language: str = 'en'
    style: str = 'general'

    def __post_init__(self):
        if self.language not in ('zh', 'en'):
            raise ValueError('unsupported language')
        if self.style not in ('general', 'professional'):
            raise ValueError('unsupported block style')

_ACTIVE = DisplayProfile()

def current_profile():
    return _ACTIVE

def use_profile(language: str, style: str):
    global _ACTIVE
    _ACTIVE = DisplayProfile(language, style)
    return _ACTIVE

_ZH_KINDS = {
 'var':'定义变量','assign':'设置变量','member':'设置成员','method':'官方方法',
 'call':'调用函数','netprop':'读取 / 修改网络属性','event':'游戏事件',
 'if':'如果','while':'当条件成立时重复','for':'按次数重复','entity_for':'逐个查找实体',
 'foreach':'遍历集合','raw':'自定义 Squirrel 代码','operator':'运算判断',
 'math_call':'数学计算','array_op':'数组操作','summon':'生成实体','zspawn':'生成感染者','trace_line':'执行 TraceLine 射线追踪',
 'return':'返回结果','break':'结束循环','continue':'跳过当前循环','throw':'抛出异常',
}
_EN_KINDS = {
 'var':'Define variable','assign':'Set variable','member':'Set member','method':'Official method',
 'call':'Call function','netprop':'Read / write netprop','event':'Game event',
 'if':'If','while':'Repeat while','for':'Counted loop','entity_for':'Find each entity',
 'foreach':'For each item','raw':'Custom Squirrel code','operator':'Operator',
 'math_call':'Math','array_op':'Array operation','summon':'Spawn entity','zspawn':'Spawn infected (ZSpawn)','trace_line':'Run TraceLine raycast',
 'return':'Return','break':'Break','continue':'Continue','throw':'Throw',
}
_ORIGINAL = {'var':'变量定义','assign':'赋值 / 修改','member':'链式成员赋值','method':'官方方法',
 'call':'调用自定义函数','netprop':'NetProps Get/Set','event':'原版游戏事件',
 'if':'If / Else','while':'While','for':'数值 For','entity_for':'实体 For','foreach':'Foreach',
 'raw':'高级：原始代码','operator':'运算符','math_call':'Math 数学函数','trace_line':'TraceLine(table)'}

def block_caption(kind, profile=None):
    p = profile or current_profile()
    if p.style == 'professional':
        if kind == 'trace_line':return 'TraceLine(table)'
        if kind == 'zspawn':return 'ZSpawn(table)'
        if p.language == 'en':
            return _EN_KINDS.get(kind, kind)
        return _ORIGINAL.get(kind, _ZH_KINDS.get(kind,kind))
    return (_ZH_KINDS if p.language=='zh' else _EN_KINDS).get(kind, kind)

_METHOD_ZH = {
 'GetActiveWeapon':'获取当前持有的武器','GetPlayerFromUserID':'根据玩家 ID 获取玩家实体',
 'GetOrigin':'获取实体坐标','SetOrigin':'设置实体坐标',
 'GetHealth':'获取当前生命值','SetHealth':'设置当前生命值',
 'GetScriptScope':'获取实体的 ScriptScope','ValidateScriptScope':'确保实体拥有 ScriptScope',
 'IsValid':'判断实体是否有效','IsSurvivor':'判断是否为幸存者',
 'Clip1':'读取当前弹匣弹药','SetClip1':'设置当前弹匣弹药',
 'GetPropInt':'读取整数网络属性','GetPropFloat':'读取浮点网络属性',
 'GetPropIntArray':'读取整数网络属性数组元素','SetPropIntArray':'修改整数网络属性数组元素',
 'ClientPrint':'向玩家显示信息','FindByClassname':'根据实体类别查找实体',
 'GetClassname':'获取实体类别名','GetPlayerName':'获取玩家名称',
 'GiveItem':'给予物品','GiveAmmo':'给予弹药','SetClip2':'设置第二弹匣弹药',
 'SetPropInt':'设置整数网络属性', 'SetPropFloat':'设置浮点网络属性',
 'GetPropString':'读取字符串网络属性', 'SetPropString':'设置字符串网络属性',
 'printl':'输出日志','print':'输出文本',
}
_METHOD_EN = {
 'GetActiveWeapon':'Get active weapon','GetPlayerFromUserID':'Find player by user ID',
 'GetOrigin':'Get entity position','SetOrigin':'Set entity position',
 'GetHealth':'Get current health','SetHealth':'Set current health',
 'GetScriptScope':'Get entity ScriptScope','ValidateScriptScope':'Ensure entity ScriptScope exists',
 'IsValid':'Check entity validity','IsSurvivor':'Check whether survivor',
 'Clip1':'Get ammo in magazine','SetClip1':'Set ammo in magazine',
 'GetPropInt':'Read integer netprop','GetPropFloat':'Read float netprop',
 'GetPropIntArray':'Read integer netprop array element',
 'SetPropIntArray':'Set integer netprop array element',
 'ClientPrint':'Display message to player','FindByClassname':'Find entity by classname',
}
_VERB_ZH = {'Get':'获取','Set':'设置','Is':'判断','Has':'检查','Find':'查找',
 'Give':'给予','Remove':'移除','Create':'创建','Spawn':'生成','Add':'添加',
 'Delete':'删除','Print':'打印','Apply':'应用','Take':'扣除','Use':'使用',
 'Clear':'清除','Send':'发送','Enable':'启用','Disable':'禁用'}

def human_words(name):
    return ' '.join(re.sub(r'([a-z0-9])([A-Z])',r'\1 \2',name).replace('_',' ').split())

def method_caption(name, profile=None, owner=''):
    p = profile or current_profile()
    if p.style == 'professional':return name
    from .friendly_labels import method_zh, method_en
    return method_zh(name,owner) if p.language=='zh' else method_en(name,owner)

_EVENT_ZH = {
 'weapon_fire':'玩家开火','weapon_reload':'玩家开始换弹','player_hurt':'玩家受到伤害',
 'player_death':'玩家死亡','player_spawn':'玩家生成','player_activate':'玩家实体激活',
 'ability_use':'特殊感染者使用能力','item_pickup':'玩家拾取物品',
 'ammo_pickup':'玩家补充弹药','heal_success':'玩家成功治疗','revive_success':'成功扶起队友',
 'infected_hurt':'普通感染者或 Witch 受到伤害','infected_death':'感染者死亡',
 'tank_spawn':'Tank 出现','witch_spawn':'Witch 出现','round_start':'回合开始',
 'round_end':'回合结束','map_transition':'切换章节',
 'defibrillator_used':'除颤器复活成功',
}
_EVENT_WORD_ZH = {'weapon':'武器','player':'玩家','infected':'感染者','survivor':'幸存者',
 'tank':'Tank','witch':'Witch','round':'回合','spawn':'生成','death':'死亡',
 'hurt':'受伤','fire':'开火','reload':'换弹','used':'使用','use':'使用','pickup':'拾取',
 'start':'开始','end':'结束','success':'成功','fail':'失败','kill':'击杀',
 'revive':'救起','item':'物品','ammo':'弹药','heal':'治疗',
 'bot':'Bot','team':'队伍','jump':'跳跃','door':'门','open':'开启','close':'关闭',
 'vote':'投票','ability':'能力','charger':'Charger','hunter':'Hunter',
 'smoker':'Smoker','jockey':'Jockey','boomer':'Boomer','spitter':'Spitter'}

def event_caption(name, profile=None):
    p = profile or current_profile()
    if p.style == 'professional':return name
    from .friendly_labels import event_zh, event_en
    return event_zh(name) if p.language=='zh' else event_en(name)

_ZH_ARGS = {'player':'玩家','userid':'玩家 ID','amount':'数量','value':'数值',
 'message':'消息内容','destination':'消息目标','ent':'实体','entity':'实体',
 'classname':'实体类别','name':'名称','target':'对象','position':'坐标',
 'origin':'坐标','propertyName':'属性名称','arrayElement':'数组下标',
 'scope':'作用域','weapon':'武器','radius':'半径','previous':'上一个实体',
 'input':'输入','context':'上下文'}

def parameter_caption(name, profile=None):
    p=profile or current_profile()
    if p.style=='professional':return name
    if p.language=='zh':return _ZH_ARGS.get(name,name)
    return human_words(name).lower()

def field_caption(key, profile=None):
    p=profile or current_profile()
    zh={'target':'目标','value':'值','condition':'条件','source':'集合','variable':'变量',
        'env':'事件数据','parameters':'参数','output':'结果变量','name':'名称',
        'key':'索引 / 键名','left':'左操作数','right':'右操作数','filter':'筛选条件',
        'event':'事件','method':'方法','infected_type':'感染者种类','pos':'生成位置','start':'起点','end':'终点','ignore':'忽略实体','mask':'碰撞掩码'}
    en={'target':'Target','value':'Value','condition':'Condition','source':'Collection',
        'variable':'Variable','env':'Event data','parameters':'Arguments','output':'Result',
        'name':'Name','key':'Index / key','left':'Left operand','right':'Right operand',
        'filter':'Filter','event':'Event','method':'Method','infected_type':'Infected type','pos':'Spawn position','start':'Start','end':'End','ignore':'Ignore','mask':'Collision mask'}
    return (zh if p.language=='zh' else en).get(key,key)

def method_field_order(profile=None):
    p=profile or current_profile()
    if p.style=='general' and p.language=='en':
        # In English, the verb phrase precedes the receiver; Chinese puts receiver first.
        return ['method','target','parameters','output']
    return ['target','method','parameters','output']

def event_field_order(profile=None):
    p=profile or current_profile()
    if p.style=='general' and p.language=='en':
        return ['event','env']
    if p.style=='general' and p.language=='zh':
        return ['event','env']
    return ['event','env']

_COMMON_WORDS_ZH = {
 'health':'生命值','max':'最大','min':'最小','current':'当前','active':'当前使用的',
 'weapon':'武器','ammo':'弹药','clip':'弹匣','reload':'换弹','primary':'主武器',
 'secondary':'副武器','item':'物品','player':'玩家','survivor':'幸存者',
 'entity':'实体','ent':'实体','origin':'位置','position':'坐标','velocity':'速度',
 'angles':'朝向','angle':'角度','forward':'前方','local':'相对','world':'世界',
 'owner':'所有者','name':'名称','class':'类型','classname':'实体类别',
 'model':'模型','size':'尺寸','scale':'缩放','body':'身体','group':'组',
 'bone':'骨骼','attachment':'附着点','sequence':'动作序列',
 'damage':'伤害','type':'类型','team':'队伍','duration':'持续时间',
 'time':'时间','distance':'距离','radius':'半径','within':'指定范围内',
 'nearest':'最近','target':'目标','area':'区域','path':'路径',
 'script':'脚本','scope':'作用域','think':'定时思考','event':'事件',
 'sound':'声音','state':'状态','flag':'标志','flags':'标志',
 'true':'真','false':'假','bool':'真假值','string':'字符串',
 'int':'整数','integer':'整数','float':'浮点数','vector':'向量',
 'alive':'存活','dead':'死亡','ghost':'幽灵','incapacitated':'倒地',
 'valid':'有效','visible':'可见','in':'在','on':'在','of':'的',
 'from':'从','to':'到','by':'按','is':'是否','has':'是否拥有',
 'get':'获取','set':'设置','find':'查找','with':'使用','first':'第一个',
 'last':'最后','next':'下一个','index':'编号','count':'数量',
 'total':'总数','button':'按键','mask':'掩码','user':'用户',
 'id':'编号','response':'响应','criteria':'条件','net':'网络',
 'prop':'属性','props':'属性','give':'给予','drop':'丢弃',
 'remove':'移除','clear':'清除','create':'创建','spawn':'生成',
 'add':'添加','update':'更新','enable':'启用','disable':'禁用',
 'touching':'接触','trigger':'触发器','data':'数据',
}
_CATEGORY_EN = {
 '变量与数据':'Variables & data','通用工具':'Utilities','自定义函数':'User functions',
 '运算与判断':'Operators & conditions','数学函数':'Math',
 '实体生成':'Entity spawning','射线追踪':'Ray tracing','NetProps':'NetProps','流程与循环':'Flow & loops',
 '高级':'Advanced','官方方法 · 按类展开':'Official methods · by class',
 '原版事件 · 按用途展开':'Game events · by purpose',
 '外部 API · 工程自定义':'External APIs · project-specific',
 '伤害与死亡':'Damage & death','物品、武器与补给':'Items, weapons & supplies',
 '特殊感染者与感染者':'Infected & special infected',
 '幸存者与玩家':'Survivors & players',
 '关卡与游戏流程':'Level & game flow','其他游戏事件':'Other events',
 '算术':'Arithmetic','比较':'Comparison','逻辑':'Logic',
 '位运算':'Bitwise',
}

def category_caption(name,profile=None):
    p=profile or current_profile()
    return name if p.language=='zh' else _CATEGORY_EN.get(name,name)

_MENU_EN = {
 '文件':'File','视图':'View','Help / 帮助':'Help','可视化':'Visual editor',
 '工具':'Tools','设置 / Settings':'Settings',
 '检查 GitHub 更新':'Check GitHub updates','启动时检查更新':'Check updates at startup',
 '新建工程':'New project','打开 .l4vp 工程':'Open .l4vp project',
 '保存工程':'Save project','工程另存为':'Save project as',
 '新建 .nut 文件':'New .nut file','导出当前 .nut':'Export current .nut',
 '批量导出工程 .nut':'Export all .nut files','导出 VPK 模组':'Export VPK addon',
 '恢复默认布局':'Restore default layout',
 '语言与模块风格 / Language & Block style':'Language & block style',
 '实体获取与组合实例':'Entity lookup examples',
 '新增分区':'Add section','新增事件监听分区':'Add event section',
 '预览 / 检查':'Preview / validate','外部自定义 API':'External APIs',
 'API 数据库信息':'API catalog information','编辑器使用指南 / Editor Guide':'Editor user guide','新建文件':'New file',
 '添加分区':'Add section','保存':'Save','生成代码':'Generate code',
 '导出 .nut':'Export .nut','编辑':'Edit','＋函数':'＋Function','＋复杂变量':'＋Complex variable',
}

def menu_caption(name,profile=None):
    p=profile or current_profile()
    return name if p.language=='zh' else _MENU_EN.get(name,name)


def descriptive_method_name(name):
    """Translate known API-name tokens conservatively, without inventing API behavior."""
    words=human_words(name).split()
    translated=[]
    known=0
    for word in words:
        value=_COMMON_WORDS_ZH.get(word.lower())
        translated.append(value if value else word)
        known+=bool(value)
    return ' '.join(translated) if known else ''
