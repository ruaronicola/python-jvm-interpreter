from .JavaClass import JavaClass
from .PrintStream import PrintStream

class System(JavaClass):
    def __init__(self):
        super().__init__()
        self.class_name = 'java/lang/System'
        self.instance_fields['out'] = self.instance_fields['err'] = PrintStream()

    def canHandleMethod(self, name, desc):
        return name in ['append', 'toString']

    def handleMethod(self, name, desc, frame):
        if name == 'append':
            v2 = str(frame.stack.pop())
            v1 = str(frame.stack.pop())
            frame.stack.pop()
            frame.stack.append(v1 + v2)
        elif name == 'toString':
            v1 = frame.stack.pop()
            frame.stack.pop()
            frame.stack.append(v1)