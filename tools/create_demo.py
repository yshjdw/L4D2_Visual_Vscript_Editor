"""Create a fully editable project demonstration inspired by Juggernaut_DLC."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from l4visual.models import Project, ScriptDocument, Section, Block
from l4visual.storage import save_project
from l4visual.codegen import SquirrelGenerator

ROOT=Path(__file__).resolve().parent.parent

def b(kind, **kwargs):return Block(kind,kwargs)
def flow(kind, args, **branches):return Block(kind,args,branches)

namespace=Section('namespace','Juggernaut_DLC',[
    b('var',name='Enhanced_Mode',value='["mutation14"]'),
    b('var',name='PendingEquip',value='true'),
    b('var',name='NextEquipCheck',value='0.0'),
    b('var',name='EnhancedArmorID',value='"juggernaut_armor_enhanced"'),
],x=40,y=55)
mutation=Section('function','If_Mutation_Ready',[
    b('var',name='mode',value='""',scope='local'),
    flow('try',{'error':'e'},body=[b('assign',target='mode',value='Convars.GetStr("mp_gamemode").tolower()')],
         catch=[b('return',value='false')]),
    flow('foreach',{'variable':'targetmode','source':'::Juggernaut_DLC.Enhanced_Mode','key':''},
         body=[flow('if',{'condition':'mode == targetmode'},body=[b('return',value='true')])]),
    b('return',value='false')
],{'owner':'Juggernaut_DLC','params':[],'return_type':'bool'},x=490,y=55)
init=Section('function','Init',[
    flow('if',{'condition':'!("ArmorSystem" in getroottable())'},body=[b('return',value='false')]),
    flow('if',{'condition':'!::ArmorSystem.Initialized'},body=[b('return',value='false')]),
    b('call',function='::ArmorSystem.RegisterArmor',parameters=['"juggernaut_armor"','5',{'kind':'multiline','value':'display_name=Juggernaut Armor\nmove_speed_penalty=0.4\ndamage_reduction=0.85'},'false'],output=''),
    b('call',function='::ArmorSystem.RegisterArmor',parameters=['"juggernaut_armor_enhanced"','0',{'kind':'multiline','value':'display_name=Juggernaut Armor Enhanced\ndamage_reduction=0.9\ndurability=9999999'},'true'],output=''),
    b('return',value='true')
],{'owner':'Juggernaut_DLC','params':[],'return_type':'bool'},x=940,y=55)
monitor=Section('think','Juggernaut_DLC_EquipThink',[
    b('var',name='now',value='Time()',scope='local'),
    flow('if',{'condition':'!::Juggernaut_DLC.PendingEquip && now < ::Juggernaut_DLC.NextEquipCheck'},body=[b('return',value='0.5')]),
    flow('if',{'condition':'::Juggernaut_DLC.CheckAllSurvivors()'},body=[
        b('assign',target='::Juggernaut_DLC.PendingEquip',value='false'),
        b('assign',target='::Juggernaut_DLC.NextEquipCheck',value='now + 2.0')]),
    b('return',value='0.5')
],{'interval':'0.5','auto_attach':True,'entity_name':'juggernaut_dlc_equip_thinker'},x=490,y=510)
check=Section('function','CheckAllSurvivors',[
    flow('if',{'condition':'!("ArmorSystem" in getroottable()) || !::ArmorSystem.Initialized'},body=[b('return',value='false')]),
    b('var',name='data',value='::ArmorSystem.LoadArmor(::Juggernaut_DLC.EnhancedArmorID)',scope='local'),
    flow('if',{'condition':'data == null'},body=[b('return',value='false')]),
    flow('entity_for',{'variable':'p','search':'FindByClassname','filter':'"player"'},body=[
        flow('if',{'condition':'!p.IsSurvivor() || p.IsDead()'},body=[b('continue')]),
        b('call',function='::ArmorSystem.SetEquipped',parameters=['p','::ArmorSystem.NewInstanceId()','::Juggernaut_DLC.EnhancedArmorID','data.durability'],output='')]),
    b('return',value='true')
],{'owner':'Juggernaut_DLC','params':[],'return_type':'bool'},x=950,y=510)
events=Section('events','Juggernaut_Events',[
    flow('event',{'event':'round_start','env':'env'},body=[b('assign',target='::Juggernaut_DLC.PendingEquip',value='true')]),
    flow('event',{'event':'player_spawn','env':'env'},body=[flow('if',{'condition':'::Juggernaut_DLC.If_Mutation_Ready()'},body=[b('assign',target='::Juggernaut_DLC.PendingEquip',value='true')])]),
    flow('event',{'event':'bot_player_replace','env':'env'},body=[b('assign',target='::Juggernaut_DLC.PendingEquip',value='true')]),
],x=40,y=525)
start=Section('init','初始化流程',[
    b('call',function='::Juggernaut_DLC.Init',parameters=[],output=''),
    b('call',function='printl',parameters=['"[Juggernaut DLC] Loaded"'],output='')
],x=40,y=1020)
project=Project('Juggernaut Demo','Juggernaut_Events',[
    ScriptDocument('juggernaut_dlc.nut',[namespace,mutation,init,monitor,check,events,start])],
    {'functions':[{'owner':'ArmorSystem','name':'RegisterArmor','params':['id','index','data','enhanced'],'returns':'void'},
                  {'owner':'ArmorSystem','name':'SetEquipped','params':['player','iid','armor','durability'],'returns':'bool'},
                  {'owner':'ArmorSystem','name':'LoadArmor','params':['armor'],'returns':'table'}]})
if __name__=='__main__':
    output=ROOT/'examples'/'Juggernaut_Demo.l4vp'
    save_project(output,project)
    code=SquirrelGenerator().compile(project,project.documents[0])
    (ROOT/'examples'/'juggernaut_dlc_generated.nut').write_text(code,encoding='utf-8')
    print('Created',output,'and .nut demonstration')
