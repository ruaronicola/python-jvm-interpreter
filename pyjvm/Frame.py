class Frame:
    def __init__(self, code, current_method, current_class, machine):
        self.code = code.code
        self.stack  = []
        self.locals = [current_class] + ['' for i in range(code.max_locals-1)]
        self.current_method = current_method
        self.current_class = current_class
        self.ip = 0
        self.machine = machine
        self.max_stack = code.max_stack

        self.set_local(0, current_class)

    def set_local(self, i, value):
        self.locals[i] = value

    def get_local(self, i):
        return self.locals[i]

    def push(self, arg):
        self.stack.append(arg)

    def pop(self):
        return self.stack.pop()