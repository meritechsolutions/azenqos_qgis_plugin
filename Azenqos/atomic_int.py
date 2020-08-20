from PyQt5 import QtCore


class atomic_int():
    mutex = QtCore.QMutex()
    val = 0
    def __init__(self, init_val):
        assert isinstance(init_val, int)
        self.val = init_val

    def get(self):    
        self.mutex.lock()
        ret = self.val
        self.mutex.unlock()
        return ret
        
    def dec_and_get(self):    
        self.mutex.lock()
        self.val -= 1
        ret = self.val
        self.mutex.unlock()
        return ret

    def inc_and_get(self):    
        self.mutex.lock()
        self.val += 1
        ret = self.val
        self.mutex.unlock()
        return ret
