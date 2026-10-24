import sys

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QMessageBox
from l4visual.ui.main_window import MainWindow
from l4visual.ui.startup_updates import StartupUpdateDialog, start_detached_install
from l4visual.display_profile import use_profile


def main():
    application = QApplication(sys.argv)
    application.setApplicationName('L4D2 Visual VScript')
    prefs = QSettings('VScript Visual Maker', 'L4D2 Visual VScript')
    # Initialize the SAME persisted language before creating the startup dialog.
    language = str(prefs.value('display/language', 'en'))
    style = str(prefs.value('display/style', 'general'))
    try:
        use_profile(language, style)
    except ValueError:
        use_profile('en', 'general')
    startup_enabled = str(prefs.value('updates/check_on_startup', 'true')).lower() not in ('false', '0', 'no')
    if startup_enabled:
        dialog = StartupUpdateDialog()
        dialog.exec()
        if dialog.install_requested and dialog.pending_update:
            archive, folder, tag = dialog.pending_update
            if dialog._check_task is not None and dialog._check_task.isRunning():
                dialog._check_task.wait(10000)
            try:
                start_detached_install(archive, folder, tag)
            except OSError as exc:
                QMessageBox.warning(None, 'Update error / 更新错误', str(exc))
            else:
                # The detached updater waits for this process to exit.
                return 0
        # The user may skip the visible check while its network request is still active.
        # Hold the object alive until shutdown, and join it only when quitting the editor.
        if dialog._check_task is not None and dialog._check_task.isRunning():
            application.aboutToQuit.connect(lambda: dialog._check_task.wait(10000))
        if dialog._download_task is not None and dialog._download_task.isRunning():
            application.aboutToQuit.connect(lambda: dialog._download_task.wait(30000))
    window = MainWindow(startup_checked=True)
    window.show()
    return application.exec()


if __name__ == '__main__':
    sys.exit(main())
