""" ThreadWaitLock version 0.0.1 """
import time
from suite.common.sysapp_common_logger import logger

class ThreadWaitLock():
    """ write/read lock for timeout """
    def __init__(self, name):
        self.name = name
        self.lockstate = True

    def get_lock_state(self):
        """ return threadlock state """
        return self.lockstate

    def poll_waitlock_timeout(self, waittime):
        """poll_waitlock_timeout """
        cnt = 0
        while self.get_lock_state() is True and cnt < waittime:
            time.sleep(1)
            cnt += 1
        if cnt >= waittime:
            logger.print_warning(f"poll {self.name} not return!")
            return False
        return True

    def lock(self):
        """ lock """
        self.lockstate = True

    def release(self):
        """ release """
        self.lockstate = False
