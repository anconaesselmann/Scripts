#! /usr/bin/python
import os
import sys
import subprocess
from console import CommandLineApplication

# commands
xcc_command = os.path.join(os.path.sep, sys.path[0], "xcc")

def create(base_name):
    command = xcc_command + ' -named"' + base_name + '"'
    print(command)
    print subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

app = CommandLineApplication()
app.install(['create', 'c'], create, 'Creates a set of view controller, view model, view model test and view files and adds them to the Xcode project.\nRequires the working directory to be the root of the Xcode project.\nTakes one argument:\nThe name with witch each of the files begins.')

try:
    app.run()
except IndexError:
    print("Error")
except ValueError as e:
    print(e)