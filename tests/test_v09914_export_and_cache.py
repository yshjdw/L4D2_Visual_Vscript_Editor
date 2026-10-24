import unittest
from pathlib import Path
from l4visual.models import Block
from l4visual.variable_types import sync_active_variable_value, reconcile_variable_cache, change_variable_type
from l4visual.ui.localization import translated_tooltip


class VariableCacheTests(unittest.TestCase):
    def test_socket_change_syncs_active_type(self):
        block=Block('var',{'name':'player','container_type':'普通','value':'GetPlayerFromUserID(env.userid)','_type_value_cache':{'普通':'env.userid.GetPlayerUserId()'}})
        sync_active_variable_value(block)
        self.assertEqual(block.args['_type_value_cache']['普通'],'GetPlayerFromUserID(env.userid)')
    def test_stale_cache_is_overwritten_on_reconciliation(self):
        block=Block('var',{'name':'player','container_type':'普通','value':'GetPlayerFromUserID(env.userid)','_type_value_cache':{'普通':'old()'}})
        reconcile_variable_cache(block)
        self.assertEqual(block.args['_type_value_cache']['普通'],block.args['value'])
    def test_switch_back_uses_latest_value(self):
        block=Block('var',{'name':'player','container_type':'普通','value':'GetPlayerFromUserID(env.userid)'})
        sync_active_variable_value(block)
        change_variable_type(None,block,'Table')
        change_variable_type(None,block,'普通')
        self.assertEqual(block.args['value'],'GetPlayerFromUserID(env.userid)')


class TooltipTests(unittest.TestCase):
    def test_long_variable_tooltip_is_english(self):
        self.assertIn('right-click',translated_tooltip('左键拖出变量引用；右键可以修改名称或选择 Table / Set 成员','en'))
    def test_variable_member_tooltip_is_english(self):
        self.assertIn('Reference:',translated_tooltip('引用：scope.ammo_keep；右键重新选择成员','en'))
    def test_zh_keeps_text(self):
        text='拖动复制已嵌入的表达式；原位置保持不变'
        self.assertEqual(translated_tooltip(text,'zh'),text)


class ExportWiringTests(unittest.TestCase):
    def test_all_export_paths_support_bypass(self):
        text=(Path(__file__).resolve().parents[1]/'l4visual/ui/main_window.py').read_text(encoding='utf-8')
        self.assertGreaterEqual(text.count('problems=[] if self.ignore_static_checks else'),3)
        self.assertIn("settings_menu.addAction(self.ignore_check_action)",text)
        self.assertIn("self.preferences.setValue('export/ignore_static_checks'",text)

if __name__=='__main__':unittest.main()
