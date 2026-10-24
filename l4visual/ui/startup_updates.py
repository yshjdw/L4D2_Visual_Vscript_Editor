"""Visible, optional GitHub update check before the editor's main window opens."""
from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys

from PySide6.QtCore import Qt, QSettings, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QMessageBox, QProgressBar,
    QPushButton, QVBoxLayout,
)

from ..update_service import RELEASES_PAGE, is_newer, update_error_text
from ..version import APP_VERSION
from ..display_profile import current_profile
from .update_tasks import ReleaseCheckTask, ReleaseDownloadTask


class StartupUpdateDialog(QDialog):
    """Startup gate: see current/check/result, or continue offline at any time."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prefs = QSettings('VScript Visual Maker', 'L4D2 Visual VScript')
        self.english = current_profile().language == 'en'
        self._check_task = None
        self._download_task = None
        self._release = None
        self._closed = False
        self._exit_when_cancelled = False
        self.install_requested = False
        self.pending_update = None

        self.setWindowTitle(self.tr_text('Check for updates', '启动前检查更新'))
        self.setMinimumWidth(540)
        self.setModal(True)
        self.setStyleSheet('''
            QDialog {background:#192436;color:#eef4fa;}
            QLabel {color:#eef4fa;}
            QPushButton {padding:7px 13px;min-height:23px;}
            QCheckBox {color:#d9e4ee;}
            QProgressBar {background:#26344a;border:1px solid #43556e;border-radius:4px;
                          text-align:center;min-height:18px;}
            QProgressBar::chunk {background:#348fc7;}
        ''')
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 22, 24, 20)

        heading = QLabel(self.tr_text('L4D2 Visual VScript Editor — Update check',
                                      'L4D2 可视化 VScript 编辑器 · 更新检查'))
        heading.setStyleSheet('font-size:19px;font-weight:650;')
        layout.addWidget(heading)
        self.current_version = QLabel(self.tr_text('Installed version: ', '当前版本：') + APP_VERSION)
        layout.addWidget(self.current_version)
        self.status = QLabel(self.tr_text('Connecting to GitHub Releases…',
                                          '正在连接 GitHub Releases…'))
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(55)
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        layout.addWidget(self.progress)
        self.details = QLabel(self.tr_text(
            'If the network is unavailable, you can enter the editor without updating.',
            '如果网络不可用，你可以跳过检查，直接进入编辑器。'))
        self.details.setWordWrap(True)
        self.details.setStyleSheet('color:#aebfd0;')
        layout.addWidget(self.details)

        self.autocheck = QCheckBox(self.tr_text('Check for updates at startup',
                                               '每次启动时检查更新'))
        self.autocheck.setChecked(True)
        self.autocheck.toggled.connect(lambda enabled:
            self.prefs.setValue('updates/check_on_startup', bool(enabled)))
        layout.addWidget(self.autocheck)

        actions = QHBoxLayout()
        layout.addLayout(actions)
        self.retry = QPushButton(self.tr_text('Retry', '重新检查'))
        self.retry.setEnabled(False)
        self.retry.clicked.connect(self.start_check)
        actions.addWidget(self.retry)
        self.open_release = QPushButton(self.tr_text('GitHub Releases', '打开发布页面'))
        self.open_release.clicked.connect(self.open_release_page)
        actions.addWidget(self.open_release)
        actions.addStretch(1)
        self.download = QPushButton(self.tr_text('Download update', '下载更新'))
        self.download.setEnabled(False)
        self.download.clicked.connect(self.start_download)
        actions.addWidget(self.download)
        self.enter = QPushButton(self.tr_text('Skip check / Enter editor', '跳过检查 / 进入编辑器'))
        self.enter.setDefault(True)
        self.enter.clicked.connect(self.enter_editor)
        actions.addWidget(self.enter)
        QTimer.singleShot(0, self.start_check)

    def tr_text(self, en, zh):
        return en if self.english else zh

    def _set_state(self, message, detail='', busy=False):
        self.status.setText(message)
        if detail:
            self.details.setText(detail)
        self.progress.setVisible(busy)
        if busy:
            self.progress.setRange(0, 0)

    def start_check(self):
        if self._closed or (self._check_task is not None and self._check_task.isRunning()):
            return
        if self._download_task is not None and self._download_task.isRunning():
            return
        self._release = None
        self.download.setEnabled(False)
        self.retry.setEnabled(False)
        self.enter.setText(self.tr_text('Skip check / Enter editor', '跳过检查 / 进入编辑器'))
        self._set_state(self.tr_text('Checking the latest GitHub Release…',
                                     '正在查询 GitHub 最新正式版本…'),
                        self.tr_text('You can skip this step and work offline.',
                                     '可以随时跳过此步骤，离线使用编辑器。'), True)
        task = ReleaseCheckTask()
        self._check_task = task
        task.found.connect(self._check_succeeded)
        task.failed.connect(self._check_failed)
        task.start()

    def _check_succeeded(self, info):
        if self._closed:
            return
        self.retry.setEnabled(True)
        self._release = info
        if not is_newer(info.version, APP_VERSION):
            if is_newer(APP_VERSION, info.version):
                label = self.tr_text('Installed version is newer than the published Release.',
                                     '当前安装版本高于 GitHub 已发布版本。')
            else:
                label = self.tr_text('You already have the latest version (' + APP_VERSION + ').',
                                     '当前已是最新版本（' + APP_VERSION + '）。')
            self._set_state(label,
                            self.tr_text('Latest published Release: ', 'GitHub 最新正式版本：') + info.version)
        elif info.asset_url:
            self._set_state(self.tr_text('A newer version is available: ', '发现新版本：') + info.version,
                            self.tr_text('Choose Download update, or enter the editor and update later.',
                                         '可以下载安装，也可以先进入编辑器，以后再更新。'))
            self.download.setEnabled(True)
        else:
            self._set_state(self.tr_text('A newer Release exists: ', '发现更新版本：') + info.version,
                            self.tr_text('The Release has no compatible editor ZIP. Open GitHub Releases to download manually.',
                                         '该 Release 没有符合要求的编辑器 ZIP；请打开发布页面检查附件。'))
        self.enter.setText(self.tr_text('Enter editor', '进入编辑器'))

    def _check_failed(self, message):
        if self._closed:
            return
        self.retry.setEnabled(True)
        self._set_state(self.tr_text('Unable to check for updates.', '检查更新失败。'),
                        update_error_text(message, 'en' if self.english else 'zh') + '\n' + self.tr_text('You can continue using the editor offline.',
                                                       '你仍可离线正常使用编辑器。'))
        self.enter.setText(self.tr_text('Enter editor', '进入编辑器'))

    def open_release_page(self):
        url = self._release.html_url if self._release else RELEASES_PAGE
        QDesktopServices.openUrl(QUrl(url))

    def start_download(self):
        if self._release is None or not self._release.asset_url:
            return
        if self._download_task is not None and self._download_task.isRunning():
            return
        self.download.setEnabled(False)
        self.retry.setEnabled(False)
        self.enter.setText(self.tr_text('Cancel download / Enter editor',
                                        '取消下载 / 进入编辑器'))
        self._set_state(self.tr_text('Downloading and verifying the editor ZIP…',
                                     '正在下载并验证编辑器 ZIP…'),
                        self.tr_text('The current installation is unchanged until the ZIP is validated.',
                                     '下载和校验完成前不会修改当前安装。'), True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        task = ReleaseDownloadTask(self._release)
        self._download_task = task
        task.progress.connect(self._download_progress)
        task.completed.connect(self._download_completed)
        task.failed.connect(self._download_failed)
        task.start()

    def _download_progress(self, value):
        if not self._closed:
            self.progress.setValue(value)

    def _download_completed(self, archive, folder):
        if self._download_task is not None:
            self._download_task.wait(2000)
        if self._closed:
            shutil.rmtree(folder, ignore_errors=True)
            return
        self._set_state(self.tr_text('Download verified successfully.',
                                     '下载完成，ZIP 校验通过。'))
        answer = QMessageBox.question(
            self,
            self.tr_text('Install update', '安装更新'),
            self.tr_text('Close the editor, install the downloaded version and restart now?\n'
                         'Your .l4vp projects will be preserved.',
                         '现在安装新版本并自动重启编辑器吗？\n不会覆盖你的 .l4vp 工程。'),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if answer == QMessageBox.Yes:
            self.pending_update = (archive, folder, self._release.tag)
            self.install_requested = True
            self._closed = True
            self.accept()
        else:
            shutil.rmtree(folder, ignore_errors=True)
            self.download.setEnabled(True)
            self.retry.setEnabled(True)
            self.enter.setText(self.tr_text('Enter editor', '进入编辑器'))

    def _download_failed(self, message):
        if self._closed and not self._exit_when_cancelled:
            return
        if self._exit_when_cancelled:
            self._closed = True
            self.accept()
            return
        self.retry.setEnabled(True)
        self.download.setEnabled(bool(self._release and self._release.asset_url))
        self._set_state(self.tr_text('Download cancelled or failed.', '下载取消或失败。'),
                        update_error_text(message, 'en' if self.english else 'zh'))
        self.enter.setText(self.tr_text('Enter editor', '进入编辑器'))

    def enter_editor(self):
        if self._download_task is not None and self._download_task.isRunning():
            self._exit_when_cancelled = True
            self._download_task.cancel()
            self.enter.setEnabled(False)
            self._set_state(self.tr_text('Cancelling download…', '正在取消下载…'), busy=True)
            return
        self._closed = True
        self.accept()

    def reject(self):
        # ESC and the title-bar X must follow the same cancellation path as Skip.
        self.enter_editor()

    def closeEvent(self, event):
        if self._download_task is not None and self._download_task.isRunning():
            self.enter_editor()
            event.ignore()
            return
        self._closed = True
        super().closeEvent(event)


def start_detached_install(archive: str, folder: str, tag: str) -> None:
    """Start update worker now; caller must then terminate this Python process."""
    current = Path(__file__).resolve()
    root = current.parents[2]
    worker_source = root / 'l4visual' / 'updater_worker.py'
    copy = Path(folder) / 'updater_worker.py'
    shutil.copy2(worker_source, copy)
    command = [sys.executable, str(copy), '--parent-pid', str(os.getpid()),
               '--install-dir', str(root), '--archive', str(archive),
               '--working-dir', str(folder), '--version', str(tag)]
    subprocess.Popen(command, cwd=str(folder),
                     creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
