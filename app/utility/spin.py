import sys
import time
import threading


class StormSpin:
    def __init__(self):
        self._done = False
        self._thread = None

    def _animate(self):
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        while not self._done:
            for cursor in chars:
                if self._done:
                    break

                sys.stdout.write(f"\r {cursor} ")
                sys.stdout.flush()
                time.sleep(0.08)

    def __enter__(self):
        self._done = False
        self._thread = threading.Thread(target=self._animate)
        self._thread.daemon = True
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._done = True
        if self._thread:
            self._thread.join()

        sys.stdout.write("\r\033[K") 
        sys.stdout.flush()
