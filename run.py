#!/usr/bin/env python

import ast
import sys

from asyncio import get_event_loop

from pyjvm.Machine import Machine
from pyjvm.jstdlib.StdlibLoader import load_stdlib_classes

from prompt_toolkit import Application
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app


# create the key bindings for prompt_toolkit
kb = KeyBindings()

@kb.add('c-c')
def exit_(event):
    event.app.exit()
    
@kb.add('c-m')
def step_(event):
    global JVM
    
    try:
        layout = next(JVM)
        event.app.layout = layout
    except StopIteration:
        event.app.exit()

    
# parse arguments
if len(sys.argv) != 4:
    print(f'Usage: {sys.argv[0]} <.class file> <function> <python repr(arguments)>')
class_file = sys.argv[1]
function = sys.argv[2]
arguments = ast.literal_eval(sys.argv[3])

# load the class file
jvm = Machine()
load_stdlib_classes(jvm)
jvm.load_class_file(class_file)

# start the JVM (as a Layout object generator)
JVM = jvm.call_function(function, arguments)
        

# create and start the application
layout = Layout(TextArea(text='Press ENTER to step to the next instruction. Press CTRL-c to exit.'))
app = Application(key_bindings=kb, layout=layout, full_screen=True)
app.run()
