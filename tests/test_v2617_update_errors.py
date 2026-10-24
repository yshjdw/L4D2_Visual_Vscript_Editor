from __future__ import annotations
import io
from pathlib import Path
import unittest
import urllib.error
from unittest.mock import patch
from l4visual.update_service import UpdateError, check_latest_release, update_error_text

class _Opener:
    def __init__(self, error):
        self.error = error
    def open(self, request, timeout=8.0):
        raise self.error


class ErrorLocalizationTests(unittest.TestCase):
    def test_quota_403_in_english_and_chinese(self):
        err = UpdateError('GitHub returned HTTP 403.', code='rate_limited')
        self.assertIn('rate limit', update_error_text(err, 'en'))
        self.assertIn('次数达到上限', update_error_text(err, 'zh'))
        self.assertNotIn('GitHub returned HTTP', update_error_text(err, 'zh'))

    def test_forbidden_not_assumed_to_be_rate_limit(self):
        err = UpdateError('GitHub returned HTTP 403.', code='forbidden')
        self.assertIn('代理', update_error_text(err, 'zh'))
        self.assertNotIn('次数达到上限', update_error_text(err, 'zh'))

    def test_403_headers_classify_rate_limit(self):
        err = urllib.error.HTTPError('https://api.github.com',403,'Forbidden',
            {'X-RateLimit-Remaining':'0', 'X-RateLimit-Reset':'1792832400'},
            io.BytesIO(b'{"message":"API rate limit exceeded"}'))
        with patch('l4visual.update_service._OPENER',_Opener(err)):
            with self.assertRaises(UpdateError) as caught:
                check_latest_release()
        self.assertEqual(caught.exception.code,'rate_limited')
        self.assertIn('UTC', update_error_text(caught.exception,'en'))

    def test_403_access_denied_no_quota_signal(self):
        err = urllib.error.HTTPError('https://api.github.com',403,'Forbidden',
            {'X-RateLimit-Remaining':'59'},io.BytesIO(b'{"message":"Resource blocked"}'))
        with patch('l4visual.update_service._OPENER',_Opener(err)):
            with self.assertRaises(UpdateError) as caught:
                check_latest_release()
        self.assertEqual(caught.exception.code,'forbidden')

    def test_prelaunch_profile_before_dialog(self):
        root=Path(__file__).resolve().parents[1]
        app=(root/'app.py').read_text(encoding='utf8')
        startup=(root/'l4visual/ui/startup_updates.py').read_text(encoding='utf8')
        self.assertLess(app.index('use_profile(language, style)'), app.index('dialog = StartupUpdateDialog()'))
        self.assertIn('current_profile().language',startup)
        self.assertIn('update_error_text(message',startup)

    def test_main_window_uses_localized_update_errors(self):
        root=Path(__file__).resolve().parents[1]
        main=(root/'l4visual/ui/main_window.py').read_text(encoding='utf8')
        self.assertIn('update_error_text(message, current_profile().language)',main)

if __name__=='__main__': unittest.main()
