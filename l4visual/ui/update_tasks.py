"""Non-blocking GitHub release check/download tasks for the PySide6 interface."""
from __future__ import annotations

import threading
from PySide6.QtCore import QThread, Signal
from ..update_service import check_latest_release, download_release


class ReleaseCheckTask(QThread):
    found = Signal(object)
    failed = Signal(object)

    def run(self):
        try:
            self.found.emit(check_latest_release())
        except Exception as exc:
            self.failed.emit(exc)


class ReleaseDownloadTask(QThread):
    progress = Signal(int)
    completed = Signal(object, object)
    failed = Signal(object)

    def __init__(self, info):
        super().__init__()
        self.info = info
        self.cancel_event = threading.Event()

    def cancel(self):
        self.cancel_event.set()

    def run(self):
        try:
            def report(downloaded, total):
                denominator = total if total else max(downloaded, 1)
                self.progress.emit(min(99, round(downloaded * 100 / denominator)))
            archive, folder = download_release(self.info, report, self.cancel_event)
            self.progress.emit(100)
            self.completed.emit(str(archive), str(folder))
        except Exception as exc:
            self.failed.emit(exc)
