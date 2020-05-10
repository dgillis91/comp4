from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

class TargetWriter:
    def write(self, msg):
        raise NotImplementedError()


class StandardOutTargetWriter(TargetWriter):
    def write(self, msg):
        print(msg)


class FileTargetWriter(TargetWriter):
    def __init__(self, path):
        self.file = open(path, 'w')
    
    def write(self, msg):
        self.file.write('{}\n'.format(msg))