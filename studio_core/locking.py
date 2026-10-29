"""Reentrant thread and process lock for the shared GUI/CLI project service."""
import os
import threading


class FileLock:
    def __init__(self, path):
        self.path = path
        self.thread_lock = threading.RLock()
        self.local = threading.local()

    def __enter__(self):
        self.thread_lock.acquire()
        depth = getattr(self.local, "depth", 0)
        try:
            if depth == 0:
                stream = open(self.path, "a+b")
                if os.name == "nt":
                    import msvcrt
                    stream.seek(0); stream.write(b"0"); stream.flush(); stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_EX)
                self.local.stream = stream
            self.local.depth = depth + 1
            return self
        except BaseException:
            self.thread_lock.release()
            raise

    def __exit__(self, *args):
        self.local.depth -= 1
        if self.local.depth == 0:
            stream = self.local.stream
            try:
                if os.name == "nt":
                    import msvcrt
                    stream.seek(0); msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream, fcntl.LOCK_UN)
            finally:
                stream.close()
        self.thread_lock.release()
