"""Plain-language interface copy based on user-supplied L4D2 function/event docs.

This is presentation metadata, not engine semantics. Ambiguous names retain an API
identifier in the tooltip; no undocumented event behavior is asserted here.
"""
from __future__ import annotations
import re
from functools import lru_cache
from .official_docs import official_functions, official_events
from .friendly_overrides import ADDITIONAL_EVENTS, ADDITIONAL_METHODS, SCENE_LABELS, MORE_WORDS, MORE_METHODS, EVENT_EN, SUBJECT_EN, ACTION_EN, REFINED_METHODS, REFINED_EVENTS

# Deliberately human-facing descriptions, not a mechanical Get/Set/call prefix.
METHOD_ZH = {
 'GetActiveWeapon':'拿到玩家手里正在用的武器','GetPlayerFromUserID':'用事件里的玩家编号找到玩家','GetPlayerFromCharacter':'按幸存者角色找到玩家',
 'GetOrigin':'读取实体在地图上的位置','SetOrigin':'把实体移到指定位置','GetLocalOrigin':'读取实体相对于父对象的位置',
 'GetHealth':'查看实体还剩多少生命值','SetHealth':'修改实体当前生命值','GetMaxHealth':'查看实体生命值上限','SetMaxHealth':'修改生命值上限',
 'GetScriptScope':'拿到实体保存脚本数据的表','ValidateScriptScope':'为实体准备脚本数据表（没有就创建）',
 'IsValid':'这个实体或对象还有效吗？','IsSurvivor':'这是幸存者吗？','IsPlayer':'这是玩家实体吗？','IsDead':'玩家已经死亡了吗？',
 'IsDying':'玩家正在死亡过渡阶段吗？','IsIncapacitated':'幸存者现在倒地了吗？','IsHangingFromLedge':'幸存者挂在边缘吗？',
 'IsGhost':'感染者处于灵魂状态吗？','IsOnFire':'玩家身上着火了吗？','IsInCombat':'玩家正在交战吗？',
 'IsFiringWeapon':'玩家正在开火吗？','IsAdrenalineActive':'玩家的肾上腺素效果还在吗？','IsImmobilized':'玩家现在行动受限吗？',
 'IsGettingUp':'玩家正在起身吗？','IsStaggering':'玩家正在踉跄吗？','IsOnThirdStrike':'幸存者已经黑白了吗？',
 'IsDominatedBySpecialInfected':'玩家是否被特殊感染者控制？','GetSpecialInfectedDominatingMe':'是谁在控制这个幸存者？',
 'GetPlayerName':'读取玩家显示的名字','GetPlayerUserId':'读取玩家本局的 UserID','GetNetworkIDString':'读取玩家的网络身份标识',
 'GetZombieType':'查看玩家属于哪一种感染者','GetSurvivorSlot':'查看幸存者所在槽位','GetButtonMask':'读取玩家正在按的按键',
 'GetHealthBuffer':'查看幸存者的临时生命值','SetHealthBuffer':'修改幸存者的临时生命值',
 'GetSenseFlags':'读取 Bot 的感知状态','SetSenseFlags':'调整 Bot 的感知状态',
 'GiveAmmo':'给玩家的主武器补充后备弹药','GiveItem':'向玩家背包里发放物品或武器',
 'GiveItemWithSkin':'给玩家一件指定外观的武器或物品','GiveUpgrade':'给玩家的主武器安装弹药升级',
 'RemoveUpgrade':'移除玩家主武器的弹药升级','DropItem':'让玩家丢下指定物品',
 'SwitchToItem':'让玩家切换到指定物品','ReviveByDefib':'用除颤器复活玩家','ReviveFromIncap':'把倒地的幸存者扶起来',
 'Stagger':'让玩家朝指定位置反方向踉跄','HitWithVomit':'让玩家被胆汁喷中','Extinguish':'扑灭玩家身上的火',
 'UseAdrenaline':'让玩家获得肾上腺素加速效果','SnapEyeAngles':'直接调整玩家观看方向',
 'EyeAngles':'查看玩家正在朝哪个方向看','EyePosition':'查看玩家眼睛所在位置',
 'Clip1':'看看弹匣里还有几发子弹','Clip2':'看看第二弹匣还剩多少弹药',
 'GetDefaultClip1':'读取武器初始弹匣容量','GetDefaultClip2':'读取第二弹匣初始容量',
 'GetMaxClip1':'查看当前武器最多装几发','GetMaxClip2':'查看第二弹匣容量上限',
 'SetClip1':'把当前弹匣改成指定弹药数','SetClip2':'修改第二弹匣里的弹药数量',
 'GiveDefaultAmmo':'把武器弹匣恢复为默认数量','Reload':'尝试让这把武器开始换弹',
 'GetClassname':'查看实体是什么类型','GetName':'读取实体的 targetname','GetModelName':'读取实体使用的模型文件',
 'GetEntityIndex':'查看实体的索引编号','Kill':'从地图中移除这个实体','TakeDamage':'让实体受到指定伤害',
 'TakeDamageEx':'按更详细的参数让实体受伤','ApplyAbsVelocityImpulse':'给实体施加世界坐标系的速度冲量',
 'ApplyLocalAngularVelocityImpulse':'让实体围绕自身坐标轴旋转','GetVelocity':'读取实体移动速度','SetVelocity':'修改实体移动速度',
 'GetForwardVector':'查看实体正前方的方向向量','GetCenter':'读取实体边界盒的中心位置',
 'FindByClassname':'按实体类型依次查找','FindByName':'按 targetname 依次查找','FindByModel':'按模型文件依次查找',
 'FindByTarget':'查找指向指定 target 的实体','FindByClassnameNearest':'找到离指定位置最近的同类实体',
 'FindByNameNearest':'找到指定位置附近最近的同名实体',
 'FindByClassnameWithin':'在指定半径内查找某类实体','FindByNameWithin':'在指定半径内查找同名实体',
 'FindInSphere':'查找球形范围内的实体','First':'拿到列表中的第一个实体','Next':'继续访问下一个实体',
 'ClientPrint':'在指定玩家屏幕上显示一条消息','print':'在控制台输出文字','printl':'向控制台输出一行文字',
 'GetPropInt':'读取实体的整数网络属性','SetPropInt':'修改实体的整数网络属性',
 'GetPropFloat':'读取实体的浮点网络属性','SetPropFloat':'修改实体的浮点网络属性',
 'GetPropVector':'读取实体的三维向量网络属性','SetPropVector':'修改实体的三维向量网络属性',
 'GetPropString':'读取实体的文本网络属性','SetPropString':'修改实体的文本网络属性',
 'GetPropEntity':'读取网络属性指向的实体','SetPropEntity':'把网络属性指向另一个实体',
 'GetPropIntArray':'读取整数网络数组中的某一项','SetPropIntArray':'修改整数网络数组中的某一项',
 'GetPropFloatArray':'读取浮点网络数组中的某一项','SetPropFloatArray':'修改浮点网络数组中的某一项',
 'GetPropVectorArray':'读取向量网络数组中的某一项','SetPropVectorArray':'修改向量网络数组中的某一项',
 'GetPropStringArray':'读取文本网络数组中的某一项','SetPropStringArray':'修改文本网络数组中的某一项',
 'GetPropEntityArray':'读取实体引用数组中的某一项','SetPropEntityArray':'修改实体引用数组中的某一项',
 'GetPropArraySize':'查看网络属性数组有多少个元素','GetPropType':'查看网络属性的存储类型','HasProp':'实体是否存在这个网络属性？',
 'GetStr':'读取控制台变量的文字值','GetFloat':'读取控制台变量的数值','SetValue':'修改控制台变量的值',
 'GetClientConvarValue':'读取指定客户端的控制台变量',
 'SpawnEntityFromTable':'按照配置创建一个地图实体','SpawnEntityGroupFromTable':'按配置批量创建一组实体',
 'ZSpawn':'在游戏中生成指定感染者','EntFire':'向指定实体发送 I/O 指令','DoEntFire':'发送实体 I/O 指令',
 'GetPlayerFromUserID':'根据游戏事件的 UserID 查找玩家实体','IncludeScript':'加载另一个 .nut 脚本文件',
 'Time':'查看当前游戏时间','RandomFloat':'在指定范围随机取小数','RandomInt':'在指定范围随机取整数',
 'sqrt':'计算平方根','pow':'计算乘方','abs':'取整数绝对值','fabs':'取小数绝对值',
 'ceil':'向上取整','floor':'向下取整','sin':'计算正弦值','cos':'计算余弦值','tan':'计算正切值',
 'asin':'计算反正弦','acos':'计算反余弦','atan':'计算反正切','atan2':'根据两个分量计算方向角',
 'exp':'计算自然指数','log':'计算自然对数','log10':'计算常用对数',
 'format':'按占位符拼接格式化字符串','split':'按分隔符拆分字符串','strip':'清除字符串首尾的指定字符',
 'lstrip':'清除字符串开头的指定字符','rstrip':'清除字符串结尾的指定字符',
 'Length':'计算向量的长度','LengthSqr':'计算向量长度的平方','Dot':'计算两个向量的点积','Cross':'计算向量叉积',
 'Norm':'把向量归一化','Scale':'按倍率缩放向量',
 'ConnectOutput':'让实体输出触发时执行指定函数','DisconnectOutput':'取消实体输出与函数的连接',
 'PrecacheModel':'提前加载模型，避免使用时卡顿','PrecacheSound':'提前加载声音资源',
 'PlayScene':'让角色播放一段对白或场景动画','GetAttachmentOrigin':'取得模型附着点的位置',
 'GetAttachmentAngles':'取得模型附着点的朝向','SetModelScale':'调整模型的显示大小',
 'GetSequence':'查看角色正在播放的动画序列','SetSequence':'让角色播放指定动画序列',
 'IsSequenceFinished':'当前动画播放完了吗？','LookupSequence':'按动画名称查找序列编号',
 'ResetSequence':'重新开始播放指定的动画','SetBodygroup':'切换模型指定身体部件',
 'GetBodygroup':'读取模型指定部件的外观编号','GetBoneOrigin':'读取模型骨骼的位置',
 'GetBoneAngles':'读取模型骨骼朝向',
}

EVENT_ZH = {
 'weapon_fire':'玩家按下开火键准备射击时','weapon_reload':'幸存者开始给武器换弹时',
 'weapon_fire_on_empty':'玩家扣下扳机但弹匣已空时','weapon_zoom':'玩家按下狙击枪开镜键时',
 'player_hurt':'玩家受到伤害时','player_death':'玩家或可玩感染者死亡时',
 'player_spawn':'玩家实体生成时','player_activate':'玩家实体开始生成时',
 'player_team':'玩家切换队伍时','player_bot_replace':'Bot 接管玩家角色时','bot_player_replace':'玩家接管 Bot 角色时',
 'ability_use':'特殊感染者使用技能时','item_pickup':'幸存者拾起一件物品时','ammo_pickup':'幸存者从弹药堆补充子弹时',
 'grenade_bounce':'投掷物碰到地面或其他物体时','hegrenade_detonate':'爆炸物发生爆炸时',
 'bullet_impact':'子弹命中表面时','player_jump':'玩家起跳时','player_jump_apex':'玩家跳到最高点时',
 'player_falldamage':'玩家受到坠落伤害时','player_ledge_grab':'幸存者抓住悬崖边缘时',
 'player_ledge_release':'幸存者松开悬崖边缘时',
 'infected_hurt':'普通感染者或 Witch 受到伤害时','infected_death':'普通感染者死亡时',
 'witch_spawn':'Witch 出现在地图上时','witch_killed':'Witch 被杀死时','witch_harasser_set':'Witch 被玩家惊扰时',
 'tank_spawn':'Tank 出现时','round_start':'新回合正式开始时','round_start_pre_entity':'回合初始化且实体尚未生成时',
 'round_start_post_nav':'回合开始且导航网格准备好时','round_end':'本回合结束时',
 'round_freeze_end':'回合开始前的冻结状态结束时','map_transition':'战役切换到下一章节时',
 'player_transitioned':'玩家完成跨章节切换时','mission_lost':'幸存者队伍任务失败时',
 'heal_begin':'幸存者开始使用医疗包时','heal_success':'幸存者用医疗包治疗成功时',
 'heal_end':'医疗包治疗过程结束时','heal_interrupted':'幸存者的医疗包治疗被打断时',
 'adrenaline_used':'幸存者打下肾上腺素时','pills_used':'幸存者吃下止痛药时',
 'pills_used_fail':'幸存者尝试吃止痛药但失败时',
 'defibrillator_begin':'幸存者开始使用除颤器时','defibrillator_used':'幸存者用除颤器成功救人时',
 'defibrillator_used_fail':'除颤器复活失败时','defibrillator_interrupted':'使用除颤器时被打断时',
 'revive_begin':'幸存者开始扶起倒地队友时','revive_success':'幸存者成功扶起队友时','revive_end':'扶起队友的过程结束时',
 'player_incapacitated':'幸存者被打倒地时','player_incapacitated_start':'幸存者即将倒地时',
 'player_first_spawn':'玩家首次生成角色实体时','player_left_safe_area':'玩家离开安全区域时',
 'player_entered_checkpoint':'玩家进入安全屋范围时','player_left_checkpoint':'玩家离开安全屋范围时',
 'player_shoved':'幸存者被另一个幸存者推开时','entity_shoved':'非幸存者实体被推开时',
 'player_now_it':'玩家被胆汁覆盖时','player_no_longer_it':'玩家身上的胆汁效果消失时',
 'tongue_grab':'Smoker 舌头抓住幸存者时','tongue_release':'Smoker 松开幸存者时',
 'choke_start':'Smoker 开始勒住幸存者时','choke_end':'Smoker 停止勒住幸存者时',
 'lunge_pounce':'Hunter 扑中幸存者时','pounce_end':'Hunter 结束压制幸存者时',
 'charger_charge_start':'Charger 开始冲锋时','charger_pummel_start':'Charger 开始摔打幸存者时',
 'survivor_rescued':'幸存者从救援房间被救出时','survivor_call_for_help':'幸存者在救援房间等待救援时',
 'weapon_drop':'幸存者把武器从背包里丢出来时','weapon_drop_to_prop':'幸存者放下油桶等实体物品时',
 'finale_start':'战役终局事件开始时','finale_escape_start':'终局逃脱阶段开始时',
 'finale_vehicle_incoming':'终局逃生载具即将到达时','finale_vehicle_ready':'终局逃生载具可以上车时',
 'finale_vehicle_leaving':'终局逃生载具准备离开时','finale_win':'幸存者完成终局并获胜时',
 'door_open':'玩家打开门时','door_close':'玩家把门关上时','door_unlocked':'门被解锁时',
 'rescue_door_open':'救援房间的门打开时',
 'vote_started':'玩家发起投票时','vote_changed':'投票票数发生变化时','vote_passed':'投票通过时',
 'vote_failed':'投票未通过时','vote_cast_yes':'玩家投下赞成票时','vote_cast_no':'玩家投下反对票时',
}

# The parser cannot derive accurate game semantics for undocumented symbols. For
# such items the label is a cautious action summary, while tooltips retain the
# exact source text. Do not use meaningless "call xxx" / "when xxx happens".
WORD_ZH = {
 'health':'生命值','max':'最大','min':'最小','current':'当前','active':'当前使用的','weapon':'武器',
 'ammo':'弹药','clip':'弹匣','reload':'换弹','primary':'主武器','secondary':'副武器',
 'item':'物品','player':'玩家','survivor':'幸存者','infected':'感染者','entity':'实体',
 'origin':'位置','position':'位置','velocity':'速度','angles':'朝向','angle':'角度',
 'owner':'所有者','name':'名称','class':'类别','classname':'实体类别','model':'模型',
 'scale':'大小','body':'身体','group':'组','bone':'骨骼','attachment':'附着点',
 'sequence':'动画','damage':'伤害','type':'类型','team':'队伍','duration':'时长',
 'time':'时间','distance':'距离','radius':'半径','target':'目标','area':'区域',
 'path':'路径','script':'脚本','scope':'作用域','event':'事件','sound':'声音',
 'state':'状态','flag':'标志','flags':'标志','valid':'有效','visible':'可见',
 'find':'查找','first':'第一个','last':'最后','next':'下一个','index':'编号',
 'count':'数量','total':'总数','button':'按键','mask':'掩码','user':'用户',
 'id':'编号','response':'响应','criteria':'条件','net':'网络','prop':'属性',
 'props':'属性','drop':'丢弃','remove':'移除','clear':'清空','create':'创建',
 'spawn':'生成','add':'添加','update':'更新','enable':'启用','disable':'停用',
 'touching':'接触','trigger':'触发器','data':'数据','random':'随机',
 'all':'所有','nearest':'最近','within':'范围内','average':'平均','averaged':'平均',
 'get':'读取','set':'调整','has':'是否拥有','is':'是否','are':'是否',
 'give':'给予','use':'使用','take':'受到','play':'播放','start':'开始',
 'stop':'停止','reset':'重置','force':'强制','register':'登记','unregister':'取消登记',
 'connect':'连接','disconnect':'断开','precache':'提前加载','apply':'施加',
 'send':'发送','print':'显示','draw':'绘制','compute':'计算', 'lookup':'查找',
 'mark':'标记','unblock':'解除阻挡','block':'阻挡','navigate':'导航',
 'nav':'导航','ladder':'梯子','surrounding':'周围','overlapping':'重叠',
 'overlap':'重叠','direction':'方向','flow':'流程进度','fog':'迷雾',
 'floor':'地板','corner':'角落','edge':'边缘','flat':'平坦','bottleneck':'瓶颈',
 'squared':'平方','sqr':'平方','top':'顶部','bottom':'底部','left':'左侧',
 'right':'右侧','parent':'父对象','child':'子对象','local':'相对',
 'world':'世界','absolute':'绝对','abs':'绝对','vector':'向量','int':'整数',
 'float':'小数','string':'文字','array':'数组','table':'数据表','size':'大小',
 'length':'长度','duration':'时长','special':'特殊','tank':'Tank','witch':'Witch',
 'boomer':'Boomer','smoker':'Smoker','hunter':'Hunter','jockey':'Jockey',
 'spitter':'Spitter','charger':'Charger','pipe':'土制炸弹','bomb':'炸弹',
 'zombie':'感染者','mob':'尸潮','survivors':'幸存者','finale':'终局','mission':'战役',
 'game':'游戏','mode':'模式','round':'回合','safe':'安全','area':'区域',
 'checkpoint':'安全屋','exit':'出口','start':'开始','end':'结束','success':'成功',
 'fail':'失败','failed':'失败','kill':'击杀','killed':'被击杀','hurt':'受伤',
 'fire':'开火','firing':'开火','shot':'射击','shove':'推搡','shoved':'被推开',
 'revive':'扶起','healing':'治疗','heal':'治疗','medkit':'医疗包',
 'bot':'Bot','vote':'投票','cast':'投出','yes':'赞成','no':'反对',
 'door':'门','open':'打开','opened':'被打开','close':'关闭','closed':'关闭',
 'use':'使用','used':'使用','pickup':'拾取','picked':'拾取','up':'起来',
 'incapacitated':'倒地','death':'死亡','dead':'死亡','alive':'存活',
 'damage':'伤害','hit':'击中','impact':'命中','bullet':'子弹','grenade':'榴弹',
 'bounce':'弹跳','detonate':'爆炸','explosion':'爆炸','vomit':'胆汁','bile':'胆汁',
 'jump':'跳跃','apex':'最高点','ledge':'悬崖边缘','fall':'坠落',
 'falling':'坠落','enter':'进入','entered':'进入','leave':'离开','left':'离开',
 'transition':'转场','transitioned':'完成转场','map':'地图','camera':'镜头',
 'final':'终局','rescue':'营救','rescued':'获救','ability':'技能',
 'begin':'开始','began':'开始','finish':'完成','finished':'完成',
 'interrupted':'被打断','interrupt':'打断','beginning':'开始',
 'spawned':'生成','pounce':'扑击','tongue':'舌头','grab':'抓住',
 'choke':'勒住','holdout':'坚守','rush':'冲锋','frustrated':'失去耐心',
 'drag':'拖拽','award':'奖励','earned':'获得','event':'事件','visible':'可见',
 'explain':'提示','radio':'无线电','connected':'连接','string':'文字',
 'spectator':'观战','host':'主机','unlocked':'解锁','locked':'锁定',
}
EVENT_SUBJECT = {'player':'玩家','weapon':'玩家的武器','survivor':'幸存者',
 'infected':'感染者','tank':'Tank','witch':'Witch','charger':'Charger',
 'jockey':'Jockey','hunter':'Hunter','smoker':'Smoker','boomer':'Boomer',
 'spitter':'Spitter','door':'门','round':'回合','vote':'投票',
 'finale':'终局','item':'物品','ammo':'弹药','map':'地图','entity':'实体',
 'upgrade':'弹药升级','heal':'治疗','revive':'扶人','pounce':'扑击',
 'tongue':'Smoker 的舌头','choke':'勒住幸存者的行为'}
EVENT_ACTION = {'fire_on_empty':'尝试用空弹匣射击','fire':'开火',
 'reload':'开始换弹','death':'死亡','hurt':'受伤','spawn':'生成','spawned':'出现',
 'start':'开始','end':'结束','used':'被使用','use':'被使用','pickup':'被拾起',
 'drop':'被丢下','killed':'被击杀','kill':'击杀目标','begin':'开始','success':'成功',
 'fail':'失败','failed':'失败','interrupted':'被打断','open':'被打开','close':'被关上',
 'left':'离开','entered':'进入','activated':'激活','ready':'准备就绪',
 'leaving':'开始离开','incoming':'即将到达','win':'获胜','jump':'跳跃',
 'pounce':'扑中目标','grab':'抓住目标','release':'放开目标',
 'changed':'发生变化','passed':'通过','voted':'完成投票',
 'end_message':'显示结束消息','visible':'进入视线'}

# For source text with no game-specific explanation, produce a conservative
# plain-language clue from identifier, not a fabricated official behavior.
def _words(name):
    name=re.sub(r'([a-z0-9])([A-Z])',r'\1 \2',name.replace('_',' '))
    return [w for w in name.split() if w]

WORD_ZH.update(MORE_WORDS)

def _summary(words):
    return ''.join(WORD_ZH.get(word.lower(),word) for word in words)

def method_zh(name,owner=''):
    qualified=(owner+'.'+name) if owner else name
    if qualified in REFINED_METHODS:return REFINED_METHODS[qualified]
    if name in REFINED_METHODS:return REFINED_METHODS[name]
    if name in METHOD_ZH:return METHOD_ZH[name]
    if name in ADDITIONAL_METHODS:return ADDITIONAL_METHODS[name]
    if name in MORE_METHODS:return MORE_METHODS[name]
    words=_words(name)
    if not words:return '未命名功能'
    verb=words[0].lower()
    noun=_summary(words[1:])
    predicate={'get':'查看','set':'调整','is':'是否','has':'是否拥有','are':'是否',
      'find':'找到','give':'给予','remove':'移除','add':'添加','clear':'清空',
      'create':'创建','spawn':'生成','force':'强制','reset':'重置','apply':'施加',
      'register':'登记','unregister':'取消登记','connect':'连接','disconnect':'断开',
      'debug':'调试','mark':'标记','unblock':'解除阻挡','print':'打印',
      'draw':'绘制','send':'发送','precache':'预加载','play':'播放','stop':'停止',
      'check':'检查','compute':'计算','lookup':'查找','lookup':'查找',
      'override':'临时覆盖','take':'造成','set':'设置','use':'使用'}
    if verb in ('is','are','has'):
        return f'{noun}吗？' if noun else f'{name} 的状态是什么？'
    if verb in predicate and noun:
        return predicate[verb]+noun
    if len(words)>=2:
        return _summary(words)
    # One-word API may already describe an action, e.g. Reload(), Dot().
    return WORD_ZH.get(verb,name)

def event_zh(name):
    if name in REFINED_EVENTS:return REFINED_EVENTS[name]
    if name in EVENT_ZH:return EVENT_ZH[name]
    if name in ADDITIONAL_EVENTS:return ADDITIONAL_EVENTS[name]
    if name.startswith('explain_'):
        subject=SCENE_LABELS.get(name[len('explain_'):])
        return ('游戏弹出“'+subject+'”的操作提示时') if subject else ('游戏弹出关于“'+_summary(name[8:].split('_'))+'”的教学提示时')
    parts=name.lower().split('_')
    if not parts:return '未命名的游戏情况'
    # Resolve longer action suffixes before single-word action suffixes.
    for split in range(1,len(parts)):
        action='_'.join(parts[split:])
        if action in EVENT_ACTION:
            subject=''.join(EVENT_SUBJECT.get(p, WORD_ZH.get(p,p)) for p in parts[:split])
            phrase=EVENT_ACTION[action]
            return f'{subject}{phrase}时'
    subject=EVENT_SUBJECT.get(parts[0],WORD_ZH.get(parts[0],parts[0]))
    rest=_summary(parts[1:])
    return f'{subject}{rest}时' if rest else f'{subject}的状态更新时'

def method_en(name,owner=''):
    from .display_profile import human_words
    words=human_words(name)
    if name in ('GetActiveWeapon','GetPlayerFromUserID','GetScriptScope','ValidateScriptScope'):
        return {'GetActiveWeapon':'Get the weapon this player is holding',
                'GetPlayerFromUserID':'Find a player using their user ID',
                'GetScriptScope':'Get this entity’s script data table',
                'ValidateScriptScope':'Ensure this entity has a script data table'}[name]
    doc=official_functions().get(owner+'.'+name)
    if doc:
        description=(doc.get('description') or '').strip().split('\n')[0]
        if description and description.lower() not in ('none','unknown'):
            first=re.split(r'(?<=[.!?])\s+',description)[0]
            return first[:145].rstrip(' .')
    return words

def event_en(name):
    if name in EVENT_EN:return EVENT_EN[name]
    doc=official_events().get(name)
    if doc:
        description=(doc.get('description') or '').strip().split('\n')[0]
        for prefix in ('Called: Fires when ','Fires when ','When '):
            if description.startswith(prefix):
                text=description[len(prefix):].strip(' .')
                if text:return 'When '+text[0].lower()+text[1:]
    if name.startswith('explain_'):
        return 'When the game offers a tip about '+name[len('explain_'):].replace('_',' ')
    words=name.lower().split('_')
    if not words:return 'Unnamed game event'
    subject=SUBJECT_EN.get(words[0], words[0].replace('_',' '))
    action='_'.join(words[1:])
    for suffix,verb in sorted(ACTION_EN.items(),key=lambda kv:-len(kv[0])):
        if action==suffix:return 'When '+subject+' '+verb
    if action:return 'When '+subject+' '+action.replace('_',' ')
    return name

@lru_cache(maxsize=1)
def comprehensive_coverage():
    """Names covered by the on-disk source, for offline audits/tests."""
    return {
        'methods':tuple(sorted(official_functions())),
        'events':tuple(sorted(official_events())),
    }
