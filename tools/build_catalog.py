"""离线构建经来源核对的初版检索库；不是游戏完整原生数据库。"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'resources' / 'catalog.sqlite3'
EVENT_SRC = 'https://wiki.alliedmods.net/Left_4_Dead_2_Events'
API_SRC = 'https://vscript.l4d2node.org/'
PROP_SRC = 'https://netprops.l4d2node.org/'

# Event names transcribed from the AlliedModders L4D2 event reference TOC.
EVENT_NAMES = '''player_death player_hurt player_team player_bot_replace bot_player_replace player_afk weapon_fire weapon_fire_on_empty weapon_reload weapon_zoom ability_use ammo_pickup item_pickup golden_crowbar_pickup grenade_bounce hegrenade_detonate bullet_impact player_footstep player_jump player_blind player_falldamage player_ledge_grab player_ledge_release door_moving door_open door_close door_unlocked rescue_door_open waiting_checkpoint_door_used waiting_door_used_versus waiting_checkpoint_button_used success_checkpoint_button_used round_freeze_end round_start_pre_entity round_start_post_nav nav_blocked nav_generate round_end_message round_end vote_ended vote_started vote_changed vote_passed vote_failed vote_cast_yes vote_cast_no infected_hurt infected_death hostname_changed difficulty_changed finale_start finale_rush finale_escape_start finale_vehicle_incoming finale_vehicle_ready finale_vehicle_leaving finale_win mission_lost finale_radio_start finale_radio_damaged final_reportscreen map_transition player_transitioned heal_begin heal_success heal_end heal_interrupted ammo_pack_used give_weapon pills_used pills_used_fail ammo_pack_used_fail_no_weapon ammo_pack_used_fail_full ammo_pack_used_fail_doesnt_use_ammo ammo_pile_weapon_cant_use_ammo defibrillator_begin defibrillator_used defibrillator_used_fail defibrillator_interrupted upgrade_pack_begin upgrade_pack_used upgrade_item_already_used upgrade_failed_no_primary dead_survivor_visible adrenaline_used revive_begin revive_success revive_end drag_begin drag_end player_incapacitated player_incapacitated_start player_entered_start_area player_first_spawn player_left_start_area player_left_safe_area player_entered_checkpoint player_left_checkpoint player_shoved entity_shoved player_jump_apex player_blocked player_now_it player_no_longer_it witch_harasser_set witch_spawn witch_killed tank_spawn melee_kill area_cleared award_earned tongue_grab tongue_broke_bent tongue_broke_victim_died tongue_release choke_start choke_end choke_stopped tongue_pull_stopped lunge_shove lunge_pounce pounce_end pounce_stopped pounce_attempt_stopped fatal_vomit survivor_call_for_help survivor_rescued survivor_rescue_abandoned relocated respawning tank_frustrated weapon_given weapon_drop weapon_drop_to_prop break_breakable achievement_earned spec_target_updated spawner_give_item create_panic_event explain_pills explain_weapons entity_visible weapon_spawn_visible boomer_near explain_pre_radio started_pre_radio explain_radio explain_gas_truck explain_panic_button explain_elevator_button explain_lift_button explain_church_door explain_emergency_door explain_crane explain_bridge explain_gas_can_panic explain_van_panic explain_mainstreet explain_train_lever explain_disturbance explain_scavenge_goal explain_scavenge_leave_area begin_scavenge_overtime scavenge_round_start scavenge_round_halftime scavenge_round_finished scavenge_score_tied versus_round_start gascan_pour_blocked gascan_pour_completed gascan_dropped gascan_pour_interrupted scavenge_match_finished versus_match_finished use_target player_use friendly_fire gameinstructor_draw gameinstructor_nodraw request_weapon_stats player_talking_state weapon_pickup hunter_punched hunter_headshot zombie_ignited boomer_exploded non_pistol_fired weapon_fire_at_40 total_ammo_below_40 player_hurt_concise tank_killed tank_rock_killed achievement_write_failed ghost_spawn_time survival_at_30min survival_at_10min explain_pre_drawbridge explain_drawbridge explain_perimeter explain_deactivate_alarm explain_impound_lot explain_decon explain_mall_window explain_mall_alarm explain_coaster explain_coaster_stop explain_decon_wait gauntlet_finale_start explain_float explain_ferry_button explain_hatch_button explain_shack_button upgrade_incendiary_ammo upgrade_explosive_ammo receive_upgrade explain_vehicle_arrival mounted_gun_start mounted_gun_overheated explain_burger_sign explain_carousel_button explain_carousel_destination explain_stage_lighting explain_stage_finale_start explain_stage_survival_start ability_out_of_range explain_stage_pyrotechnics explain_c3m4_radio1 explain_c3m4_radio2 explain_gates_are_open explain_c2m4_ticketbooth explain_c3m4_rescue explain_hotel_elevator_doors explain_gun_shop_tanker explain_gun_shop explain_store_alarm explain_store_item explain_store_item_stop explain_survival_generic explain_survival_alarm explain_survival_radio explain_survival_carousel explain_return_item explain_save_items spit_burst entered_spit temp_c4m1_getgas temp_c4m3_return_to_boat explain_c1m4_finale c1m4_scavenge_instructions punched_clown charger_killed spitter_killed jockey_ride jockey_ride_end jockey_punched jockey_headshot jockey_killed non_melee_fired infected_decapitated upgrade_pack_added vomit_bomb_tank triggered_car_alarm panic_event_finished charger_charge_start charger_charge_end charger_carry_start charger_carry_end charger_carry_kill charger_impact charger_pummel_start charger_pummel_end strongman_bell_knocked_off molotov_thrown gas_can_forced_drop explain_need_gnome_to_continue explain_survivor_glows_disabled explain_item_glows_disabled explain_rescue_disabled explain_bodyshots_reduced explain_witch_instant_kill set_instructor_group_enabled stashwhacker_game_won'''.split()
# Three commonly used baseline events are from Source's shared event references, not the above L4D2-specific TOC.
EVENT_NAMES += ['round_start','player_spawn','player_disconnect','player_connect']
FIELDS = {
 'player_death': 'userid:int,entityid:int,attacker:int,attackername:string,attackerentid:int,weapon:string,headshot:bool,attackerisbot:bool,victimname:string,victimisbot:bool,abort:bool,type:int,victim_x:float,victim_y:float,victim_z:float',
 'player_hurt': 'userid:int,attacker:int,attackerentid:int,health:int,armor:int,weapon:string,dmg_health:int,dmg_armor:int,hitgroup:int,type:int',
 'player_team': 'userid:int,team:int,oldteam:int,disconnect:bool,name:string,isbot:bool',
 'player_bot_replace': 'player:int,bot:int', 'bot_player_replace':'bot:int,player:int',
 'player_spawn':'userid:int', 'player_disconnect':'userid:int',
 'player_incapacitated_start':'userid:int,attacker:int,attackerentid:int,weapon:string,type:int',
 'player_first_spawn':'userid:int,map_name:string,isbot:bool',
 'weapon_fire':'userid:int,weapon:string,weaponid:int',
 'weapon_reload':'userid:int', 'item_pickup':'userid:int,item:string',
 'weapon_pickup':'userid:int', 'infected_hurt':'attacker:int,entityid:int,hitgroup:int,amount:int,type:int',
 'infected_death':'attacker:int,infected_id:int,gender:int,weapon_id:int,headshot:bool,minigun:bool,blast:bool,submerged:bool',
 'tank_killed':'userid:int,attacker:int,solo:bool,melee_only:bool,l4d1_only:bool',
 'round_end':'winner:int,reason:int,message:string,time:float',
 'nav_blocked':'area:int,blocked:bool',
 'witch_killed':'userid:int,witchid:int,oneshot:bool',
}

# Class method names and return types checked against L4D2node VScript class pages.
# "parameters" may be partially specified; uncertain signatures are left as free-form in UI.
METHODS = {
 'CEntities': {'FindByClassname':('hscript','previous:hscript,classname:string'),'FindByClassnameNearest':('hscript','classname:string,origin:Vector,distance:float'),'FindByClassnameWithin':('hscript','previous:hscript,classname:string,origin:Vector,distance:float'), 'FindByModel':('hscript','previous:hscript,model:string'), 'FindByName':('hscript','previous:hscript,name:string'),'FindByNameNearest':('hscript','name:string,origin:Vector,distance:float'),'FindByNameWithin':('hscript','previous:hscript,name:string,origin:Vector,distance:float'),'FindByTarget':('hscript','previous:hscript,name:string'),'FindInSphere':('hscript','previous:hscript,origin:Vector,distance:float'),'First':('hscript',''),'Next':('hscript','previous:hscript')},
 'Convars': {'GetClientConvarValue':('string','name:string,entindex:int'),'GetFloat':('float','name:string'),'GetStr':('string','name:string'),'SetValue':('void','name:string,value:string')},
 'CBaseEntity': {'ApplyAbsVelocityImpulse':('void','value:Vector'), 'ApplyLocalAngularVelocityImpulse':('void','value:Vector'),'ConnectOutput':('void','output:string,callback:string'),'DisconnectOutput':('void','output:string,callback:string'),'FirstMoveChild':('hscript',''), 'GetAngles':('QAngle',''),'GetBaseVelocity':('Vector',''),'GetCenter':('Vector',''),'GetClassname':('string',''),'GetContext':('unknown','name:string'),'GetEntityHandle':('hscript',''),'GetEntityIndex':('int',''),'GetForwardVector':('Vector',''),'GetHealth':('int',''),'GetLocalAngles':('QAngle',''),'GetLocalAngularVelocity':('QAngle',''),'GetLocalOrigin':('Vector',''),'GetLocalVelocity':('Vector',''),'GetMaxHealth':('int',''),'GetModelName':('string',''),'GetMoveParent':('hscript',''),'GetName':('string',''),'GetOrigin':('Vector',''),'GetOwnerEntity':('hscript',''),'GetPreTemplateName':('string',''),'GetRootMoveParent':('hscript',''),'GetScriptScope':('table',''),'GetVelocity':('Vector',''),'IsPlayer':('bool',''),'Kill':('void',''),'NextMovePeer':('hscript',''),'OverrideFriction':('void','duration:float,value:float'),'PrecacheModel':('int','model:string'),'PrecacheScriptSound':('void','sound:string'),'SetAngles':('void','angles:QAngle'),'SetContext':('void','name:string,value:string,duration:float'),'SetContextNum':('void','name:string,value:float,duration:float'),'SetForwardVector':('void','vector:Vector'),'SetFriction':('void','value:float'),'SetGravity':('void','value:float'),'SetHealth':('void','health:int'),'SetLocalAngles':('void','angles:QAngle'),'SetLocalOrigin':('void','origin:Vector'),'SetMaxHealth':('void','health:int'),'SetModel':('void','model:string'),'SetOrigin':('void','origin:Vector'),'SetVelocity':('void','velocity:Vector'),'TakeDamage':('void','damage:float,type:int,attacker:hscript'),'TakeDamageEx':('void','inflictor:hscript,attacker:hscript,weapon:hscript,force:Vector,position:Vector,damage:float,type:int'),'ValidateScriptScope':('bool','')},
 'CTerrorPlayer': {'DropItem':('void','name:string'),'Extinguish':('void',''),'EyeAngles':('QAngle',''),'EyePosition':('Vector',''),'GetActiveWeapon':('hscript',''),'GetAliveDuration':('float',''),'GetButtonMask':('int',''),'GetHealthBuffer':('float',''),'GetLastKnownArea':('hscript',''),'GetNetworkIDString':('string',''),'GetPlayerName':('string',''),'GetPlayerUserId':('int',''),'GetSenseFlags':('int',''),'GetSpecialInfectedDominatingMe':('hscript',''),'GetSurvivorSlot':('int',''),'GetZombieType':('int',''),'GiveAmmo':('void','count:int'),'GiveItem':('void','classname:string'),'GiveItemWithSkin':('void','classname:string,skin:int'),'GiveUpgrade':('void','upgrade:int'),'HasEverBeenInjured':('bool','team:int'),'HitWithVomit':('void',''),'IsAdrenalineActive':('bool',''),'IsDead':('bool',''),'IsDominatedBySpecialInfected':('bool',''),'IsDying':('bool',''),'IsFiringWeapon':('bool',''),'IsGettingUp':('bool',''),'IsGhost':('bool',''),'IsHangingFromLedge':('bool',''),'IsImmobilized':('bool',''),'IsIncapacitated':('bool',''),'IsInCombat':('bool',''),'IsIT':('bool',''),'IsOnFire':('bool',''),'IsOnThirdStrike':('bool',''),'IsStaggering':('bool',''),'IsSuppressingFallingDamage':('bool',''),'IsSurvivor':('bool','')},
 'CTerrorWeapon': {'Clip1':('int',''),'Clip2':('int',''),'GetDefaultClip1':('int',''),'GetDefaultClip2':('int',''),'GetMaxClip1':('int',''),'GetMaxClip2':('int',''),'GiveDefaultAmmo':('void',''),'Reload':('bool',''),'SetClip1':('void',''),'SetClip2':('void','')},
 'CNetPropManager': {}
}
for suffix, typ in [('Int','int'),('Float','float'),('String','string'),('Vector','Vector'),('Entity','hscript')]:
    METHODS['CNetPropManager']['GetProp'+suffix] = (typ,'entity:hscript,property:string')
    METHODS['CNetPropManager']['SetProp'+suffix] = ('void','entity:hscript,property:string,value:'+typ)
    METHODS['CNetPropManager']['GetProp'+suffix+'Array'] = (typ,'entity:hscript,property:string,index:int')
    METHODS['CNetPropManager']['SetProp'+suffix+'Array'] = ('void','entity:hscript,property:string,value:'+typ+',index:int')
METHODS['CNetPropManager'].update({'HasProp':('bool','entity:hscript,property:string'),'GetPropType':('string','entity:hscript,property:string'),'GetPropArraySize':('int','entity:hscript,property:string')})
GLOBALS = {'Time':('float',''),'GetPlayerFromUserID':('hscript','userid:int'),'SpawnEntityFromTable':('hscript','classname:string,keyvalues:table'),'AddThinkToEnt':('void','entity:hscript,name:string'),'IncludeScript':('bool','filename:string,scope:table'),'printl':('void','message:any'),'getroottable':('table',''),'Vector':('Vector','x:float,y:float,z:float'),'QAngle':('QAngle','x:float,y:float,z:float'),'EntFire':('void','target:string,input:string,value:string,delay:float'),'__CollectGameEventCallbacks':('void','scope:table'),'DoEntFire':('void','target:string,input:string,value:string,delay:float,activator:hscript,caller:hscript'),'Msg':('void','message:string')}

TABLES = {
 'DT_BaseEntity':None,'DT_BaseAnimating':'DT_BaseEntity','DT_BaseAnimatingOverlay':'DT_BaseAnimating',
 'DT_BaseFlex':'DT_BaseAnimatingOverlay','DT_BaseCombatCharacter':'DT_BaseFlex',
 'DT_BasePlayer':'DT_BaseCombatCharacter','DT_CSPlayer':'DT_BasePlayer','DT_TerrorPlayer':'DT_CSPlayer',
 'DT_SurvivorBot':'DT_TerrorPlayer','DT_BaseCombatWeapon':'DT_BaseAnimating',
 'DT_WeaponCSBase':'DT_BaseCombatWeapon','DT_TerrorWeapon':'DT_WeaponCSBase',
 'DT_TerrorGun':'DT_TerrorWeapon','DT_WeaponCSBaseGun':'DT_TerrorWeapon',
 'DT_BaseRifle':'DT_WeaponCSBaseGun','DT_AssaultRifle':'DT_BaseRifle',
 'DT_BaseShotgun':'DT_WeaponCSBaseGun','DT_BaseAutoShotgun':'DT_BaseShotgun',
 'DT_AutoShotgun':'DT_BaseAutoShotgun','DT_WeaponGrenadeLauncher':'DT_WeaponCSBaseGun',
 'DT_WeaponChainsaw':'DT_TerrorWeapon',
 'DT_AbilityBase':None, 'DT_AbilityTongue':'DT_AbilityBase',
 'DT_AbilityVomit':'DT_AbilityBase', 'DT_AbilityThrow':'DT_AbilityBase',
 'DT_Tank':'DT_TerrorPlayer','DT_Witch':'DT_BaseAnimating','DT_Boomer':'DT_TerrorPlayer',
 'DT_Charger':'DT_TerrorPlayer','DT_Hunter':'DT_TerrorPlayer','DT_Smoker':'DT_TerrorPlayer',
 'DT_Jockey':'DT_TerrorPlayer','DT_Spitter':'DT_TerrorPlayer',
 'DT_CountdownTimer':None,'DT_CollisionProperty':None,'DT_GlowProperty':None,
 'DT_LocalWeaponData':None,'DT_LocalActiveWeaponData':None,'DT_LocalActiveL4DWeaponData':None,
}
# Explicit type entries verified on corresponding DT_ pages; unknown props must be supplied by an extended data pack.
PROPS = {
 'DT_BaseEntity': 'm_flSimulationTime:int m_flCreateTime:float m_cellbits:int m_cellX:int m_cellY:int m_cellZ:int m_vecOrigin:vec3 m_nModelIndex:int m_nRenderFX:int m_nRenderMode:int m_fEffects:int m_clrRender:int m_iTeamNum:int m_CollisionGroup:int m_flElasticity:float m_flShadowCastDistance:float m_hOwnerEntity:int m_hEffectEntity:int moveparent:int m_iParentAttachment:int m_hScriptUseTarget:int movetype:int movecollide:int m_angRotation:vec3 m_iTextureFrameIndex:int m_bSimulatedEveryTick:int m_bAnimatedEveryTick:int m_bAlternateSorting:int m_Gender:int m_fadeMinDist:float m_fadeMaxDist:float m_flFadeScale:float',
 'DT_BaseCombatWeapon': 'm_iViewModelIndex:int m_iWorldModelIndex:int m_iState:int m_hOwner:int m_bInReload:int m_iClip1:int',
 'DT_BasePlayer': 'm_hVehicle:int m_hUseEntity:int m_hGroundEntity:int m_hLastWeapon:int m_hElevator:int m_iHealth:int m_lifeState:int m_iBonusProgress:int m_iBonusChallenge:int m_flMaxspeed:float m_fFlags:int m_iObserverMode:int m_hObserverTarget:int m_iFOV:int m_iFOVStart:int m_flFOVTime:float m_iDefaultFOV:int m_hZoomOwner:int',
 'DT_TerrorPlayer': 'm_mainSequenceStartTime:float m_nSequence:int m_grenadeLayerSequence:int m_fireLayerSequence:int m_flinchLayerSequence:int m_fidgetLayerSequence:int m_reloadLayerSequence:int m_reloadAltLayerSequence:int m_reloadLayerNumShells:int m_grenadeLayerStartTime:float m_fireLayerStartTime:float m_flinchLayerStartTime:float m_fidgetLayerStartTime:float m_reloadLayerStartTime:float m_reloadAltLayerStartTime:float m_hBuildableButtonUseEnt:int m_NetGestureSequence:int[7] m_NetGestureActivity:int[7] m_NetGestureStartTime:float[7] m_fServerAnimStartTime:float m_hasVisibleThreats:int m_burnPercent:float m_bbqPercent:float m_holdingObject:int m_healthBuffer:float m_healthBufferTime:float m_isGoingToDie:int m_noiseLevel:float m_noiseLevelLatch:int m_iBloodyHandsLevel:int m_bAdrenalineActive:int m_survivorCharacter:int m_zombieClass:int m_zombieState:int m_isIncapacitated:int m_isCalm:int m_useActionOwner:int m_useActionTarget:int m_iCurrentUseAction:int m_reviveOwner:int',
 'DT_SurvivorBot': 'm_nTickBase:int m_humanSpectatorUserID:int m_humanSpectatorEntIndex:int',
 'DT_TerrorWeapon': 'm_nUpgradedPrimaryAmmoLoaded:int',
}


def build():
    if DEST.exists():
        DEST.unlink()
    con = sqlite3.connect(DEST)
    con.executescript('''
    CREATE TABLE events(name TEXT PRIMARY KEY, category TEXT, fields TEXT, source TEXT);
    CREATE TABLE methods(owner TEXT, name TEXT, returns TEXT, parameters TEXT, source TEXT, PRIMARY KEY(owner,name));
    CREATE TABLE sendtables(name TEXT PRIMARY KEY, base TEXT, source TEXT);
    CREATE TABLE netprops(table_name TEXT, name TEXT, type TEXT, source TEXT, PRIMARY KEY(table_name,name));
    CREATE INDEX netprops_search ON netprops(name);
    ''')
    for event in sorted(set(EVENT_NAMES)):
        if event.startswith('player_') or event.startswith('bot_'):
            category = '玩家'
        elif event.startswith(('weapon_', 'ammo_','item_','upgrade_')):
            category = '武器物品'
        elif event.startswith(('infected_','tank_','witch_','charger_','jockey_')):
            category = '感染者'
        elif event.startswith(('round_','finale_','mission_')):
            category = '关卡'
        else:
            category = '其他'
        con.execute('INSERT INTO events VALUES(?,?,?,?)',(event,category,FIELDS.get(event,''),EVENT_SRC if event not in ('round_start','player_spawn','player_disconnect','player_connect') else 'https://wiki.alliedmods.net/Game_Events_(Source)'))
    for owner, methods in {**METHODS,'Global':GLOBALS}.items():
        for name,(returns,parameters) in methods.items():
            con.execute('INSERT INTO methods VALUES(?,?,?,?,?)',(owner,name,returns,parameters,API_SRC if owner!='Global' else 'https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Scripting/Script_Functions'))
    for name,base in TABLES.items():
        con.execute('INSERT INTO sendtables VALUES(?,?,?)',(name,base,PROP_SRC+'class/'+name))
    for table,names in PROPS.items():
        for pair in names.split():
            name, typ = pair.split(':',1)
            con.execute('INSERT INTO netprops VALUES(?,?,?,?)',(table,name,typ,PROP_SRC+'class/'+table))
    con.commit()
    print('Built',DEST)
    for t in ('events','methods','sendtables','netprops'):
        print(t,con.execute('SELECT COUNT(*) FROM '+t).fetchone()[0])
    con.close()


if __name__ == '__main__':
    build()
