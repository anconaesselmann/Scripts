import os
import sys
import json

"""
Options gets options from a json file, command line arguments or the command line prompt.
"""
class Options:
    _dir = None
    _options = None
    _ephemeral = None

    def __init__(self, dir):
        self._dir = dir
        self._options = {}
        self._ephemeral = {}

    def has(self, name, prompt, isRetained = True):
        self._options[name] = prompt
        self._ephemeral[name] = isRetained

    def get(self):
        dictionary = {}
        if os.path.isfile(self._dir):
            dictionary = json.load(open(self._dir))

        dictionary = self._get_opt_from_argv(dictionary)
        dictionary = self._get_opt_from_input(dictionary)

        with open(self._dir, 'w') as outfile:
            filtered = {}
            for key, value in dictionary.items():
                if not self._ephemeral[key]:
                    continue
                filtered[key] = value
            json.dump(filtered, outfile, indent=4, sort_keys=True)

        return dictionary

    def get_arg_from_flag(self, flag):
        flag_length = len(flag)
        for arg in sys.argv:
            if arg[:flag_length] == flag:
                return arg[flag_length:]
        return None

    def _get_opt_from_input(self, dictionary):
        for name, prompt in self._options.items():
            if not name in dictionary:
                dictionary[name] = raw_input(prompt)
        return dictionary

    def _get_opt_from_argv(self, dictionary):
        for name, prompt in self._options.items():
            value = self.get_arg_from_flag('-' + name)
            if not value == None:
                dictionary[name] = value
        return dictionary
