#! /usr/bin/python

import subprocess
import os

file_to_show = "/Applications/iTunes.app"
print subprocess.Popen('open "' + os.getcwd() + '"', shell=True, stdout=subprocess.PIPE).stdout.read()