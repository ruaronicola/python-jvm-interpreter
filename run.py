#!/usr/bin/env python

import ast
import sys
import subprocess

from asyncio import get_event_loop

from pyjvm.Machine import Machine, LAYOUT_STACK
from pyjvm.jstdlib.StdlibLoader import load_stdlib_classes

from prompt_toolkit import Application
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.widgets import Label, Frame, TextArea, Box
from prompt_toolkit.layout import Layout, Dimension, Window
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
from prompt_toolkit import prompt


# create the key bindings for prompt_toolkit
EXECUTION_INDEX = 0
CONST_POOL_INDEX = 0
CONST_POOL_PAGES = []
kb = KeyBindings()

@kb.add('q')
def exit_(event):
    event.app.exit()

@kb.add('c-c')
def exit_(event):
    event.app.exit()
    
@kb.add('g', 'g')
def goto_start_(event):
    global EXECUTION_INDEX
    
    if event.app.layout != LAYOUT_STACK[EXECUTION_INDEX]:
        return
    
    EXECUTION_INDEX = 0
    event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]
    
@kb.add('G', 'G')
def goto_end_(event):
    global EXECUTION_INDEX
    
    if event.app.layout != LAYOUT_STACK[EXECUTION_INDEX]:
        return
    
    EXECUTION_INDEX = len(LAYOUT_STACK)-1
    event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]
    
@kb.add('c-m')
def start_(event):
    global EXECUTION_INDEX
    
    event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]
    
@kb.add('v')
def exit_(event):
    global EXECUTION_INDEX, CONST_POOL_INDEX, CONST_POOL_PAGES
    
    if event.app.layout == CONST_POOL_PAGES[CONST_POOL_INDEX]:
        event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]
    else:
        event.app.layout = CONST_POOL_PAGES[CONST_POOL_INDEX]
    
@kb.add('left')
def page_previous_(event):
    global CONST_POOL_INDEX, CONST_POOL_PAGES
    
    if event.app.layout != CONST_POOL_PAGES[CONST_POOL_INDEX]:
        return
    
    if CONST_POOL_INDEX >= 1:
        CONST_POOL_INDEX -= 1
        event.app.layout = CONST_POOL_PAGES[CONST_POOL_INDEX]

@kb.add('right')
def page_next_(event):
    global CONST_POOL_INDEX, CONST_POOL_PAGES
    
    if event.app.layout != CONST_POOL_PAGES[CONST_POOL_INDEX]:
        return
    
    if CONST_POOL_INDEX < len(CONST_POOL_PAGES)-1:
        CONST_POOL_INDEX += 1
        event.app.layout = CONST_POOL_PAGES[CONST_POOL_INDEX]

@kb.add('up')
def step_previous_(event):
    global EXECUTION_INDEX
    
    if event.app.layout != LAYOUT_STACK[EXECUTION_INDEX]:
        return
    
    if EXECUTION_INDEX >= 1:
        EXECUTION_INDEX -= 1
        event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]

@kb.add('down')
def step_next_(event):
    global EXECUTION_INDEX
    
    if event.app.layout != LAYOUT_STACK[EXECUTION_INDEX]:
        return
    
    if EXECUTION_INDEX < len(LAYOUT_STACK)-1:
        EXECUTION_INDEX += 1
        event.app.layout = LAYOUT_STACK[EXECUTION_INDEX]

    
# parse arguments
# if len(sys.argv) != 4:
#     print(f'Usage: {sys.argv[0]} <.class file> <function> <python repr(arguments)>')
#     exit(1)
# class_file = sys.argv[1]
# function = sys.argv[2]
# arguments = ast.literal_eval(sys.argv[3])

if len(sys.argv) < 4:
    print(f'Usage: {sys.argv[0]} <.java file> <class> <method> [<python repr(arguments)>]')
    exit(1)
java_file = sys.argv[1]
class_name = sys.argv[2]
method_name = sys.argv[3]
if len(sys.argv) >= 5:
    arguments = ast.literal_eval(sys.argv[4])
else:
    arguments = None

# compile
try:
    subprocess.check_call(['javac', '--release', '8', java_file])
    java_basename = java_file.split('/')[-1]
    class_file = java_file.replace(java_basename, f'{class_name}.class')
except subprocess.CalledProcessError:
    print(f'Failed to compile {java_file}')
    exit(1)
    
with open(java_file, 'r') as f:
    code = f.readlines()
    
    if 'package' in code[0]:
        package = code[0].split()[-1].strip(';')
        class_name = f'{package}/{class_name}'
    method = f'{class_name}/{method_name}'


# load the class file
jvm = Machine()
load_stdlib_classes(jvm)
jvm.load_class_file(class_file)


# create layout for constant pool view
frames = [
    [Label(text=f'{i+1}:', width=5) for i,_ in enumerate(jvm.class_files[class_name].const_pool)],
    [Label(text=f'{c.tag.name if c.tag else "?"}', width=15) for c in jvm.class_files[class_name].const_pool],
    [Label(text=', '.join([f'{k}:{v}' for k,v in c.__dict__.items() if k != 'tag'])) for c in jvm.class_files[class_name].const_pool],
]
frames = [list(f) for f in zip(*frames)]

CONST_POOL_PAGES = []

for i in range(0, len(frames), 14):
    frames_chunk = frames[i:i+14]
    
    page = Layout(HSplit([
        VSplit([HSplit([Frame(VSplit(frame)) for frame in frames_chunk])]),
        Window(),
        Label('LEFT/RIGHT: change page. v: toggle view. q: quit.')
    ]))
    
    CONST_POOL_PAGES += [page]


# start the JVM and record the Layout at each step
print(f'Recording the execution of {method}...')
ERROR = False
try:
    stdout = jvm.call_function(method, arguments)
except:
    ERROR = True

if not LAYOUT_STACK:
    print('Something went wrong during the execution')
    exit(1)

# overwrite the first textbox of each Layout object to show the number of steps
for i,l in enumerate(LAYOUT_STACK):
    if ERROR:
        text = f'Step {i+1}/{len(LAYOUT_STACK)} [WARNING: PARTIAL EXECUTION]'
        style = 'class:text-area fg:red'
    else:
        text = f'Step {i+1}/{len(LAYOUT_STACK)}'
        style = 'class:text-area'
        
    l.container.children[0].children[0].children[0].children[2].children[1].get_container().children[0].content.buffer.text = text
    l.container.children[0].children[0].children[0].children[2].children[1].get_container().children[0].style = style

# create and start the application (will replay the recorded execution)
layout = LAYOUT_STACK[EXECUTION_INDEX]

app = Application(key_bindings=kb, layout=layout, full_screen=True)
app.run()
