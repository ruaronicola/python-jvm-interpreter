#!/usr/bin/env python

import ast
import sys

from asyncio import get_event_loop

from pyjvm.Machine import Machine, LAYOUT_STACK
from pyjvm.jstdlib.StdlibLoader import load_stdlib_classes

from prompt_toolkit import Application
from prompt_toolkit.widgets import Label
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app


# create the key bindings for prompt_toolkit
EXECUTION_INDEX = 0
kb = KeyBindings()

@kb.add('c-c')
def exit_(event):
    event.app.exit()
    
@kb.add('c-m')
def step_(event):
    global EXECUTION_INDEX
    
    event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]
    
@kb.add('down')
def step_(event):
    global EXECUTION_INDEX
    
    if EXECUTION_INDEX < len(LAYOUT_STACK)-1:
        EXECUTION_INDEX += 1
        event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]
        
@kb.add('up')
def step_(event):
    global EXECUTION_INDEX
    
    if EXECUTION_INDEX >= 1:
        EXECUTION_INDEX -= 1
        event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]

    
# parse arguments
if len(sys.argv) != 4:
    print(f'Usage: {sys.argv[0]} <.class file> <function> <python repr(arguments)>')
    exit(1)
class_file = sys.argv[1]
function = sys.argv[2]
arguments = ast.literal_eval(sys.argv[3])

# load the class file
jvm = Machine()
load_stdlib_classes(jvm)
jvm.load_class_file(class_file)

# start the JVM and record the Layout at each step
print('Recording the execution...')
stdout = jvm.call_function(function, arguments)

# overwrite the first textbox of each Layout object to show the number of steps
for i,l in enumerate(LAYOUT_STACK):
    l.container.children[0].children[0].children[2].children[1].get_container().children[0].content.buffer.text = f'Step {i+1}/{len(LAYOUT_STACK)}'


# create and start the application (will replay the recorded execution)
layout = Layout(Label(text='Press ENTER to start. Press UP/DOWN to step to the previous/next instruction. Press CTRL-c to exit.'))
app = Application(key_bindings=kb, layout=layout, full_screen=True)
app.run()
