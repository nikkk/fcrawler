#-*- coding:utf-8 -*-

class PushbackWrapper(object):
    def __init__(self, it):
        self.it = it
        self.pushed = []
        self.nextfn = it.next

    def __iter__(self):
        return self

    def __nonzero__(self):
        if self.pushed:
            return True
        try:
            self.pushback(self.nextfn())
        except StopIteration:
            return False
        else:
            return True

    def popfn(self):
        res = self.pushed.pop()
        if not self.pushed:
            self.nextfn = self.it.next
        return res

    def next(self):
        return self.nextfn()

    def pushback(self, x):
        self.pushed.append(x)
        self.nextfn = self.popfn
