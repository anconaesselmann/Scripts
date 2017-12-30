import sys
from textwrap import TextWrapper


def has_flags():
    if len(sys.argv) < 2:
        return False
    argv1 = sys.argv[1]
    if argv1[0] != '-':
        return False
    return True


def is_flag_set(flag):
    if not has_flags():
        return False
    flags = sys.argv[1]
    for char in flags:
        if char == flag:
            return True
    return False


def get_method():
    method_index = 1
    if has_flags():
        method_index += 1
    if len(sys.argv) < method_index + 1:
        return False
    return sys.argv[method_index]


def get_arguments():
    args_index = 2
    if has_flags():
        args_index += 1
    if len(sys.argv) < args_index + 1:
        return []
    return sys.argv[args_index:]


class CommandLineApplication:
    _methods = {}
    _default = False
    _help = {}
    _wrapper = None

    def __init__(self):
        self._wrapper = TextWrapper()
        self._wrapper.width = 60
        self._wrapper.initial_indent = '    '
        self._wrapper.subsequent_indent = '    '

    def install(self, name, method, help_text=''):
        if isinstance(name, list):
            for n in name:
                self.install(n, method)
        else:
            self._methods[name] = method

        self.create_help(name, help_text)

    def install_default(self, method):
        self._default = method

    def create_help(self, name, help_text):
        if help_text == '':
            return
        final_help_text = ''
        if isinstance(name, list):
            for n in name:
                if final_help_text == '':
                    final_help_text = n
                else:
                    final_help_text += ', ' + n
        if final_help_text == '':
            final_help_text = name
        final_help_text += ":\n" + help_text

        if isinstance(name, list):
            self._help[name[0]] = final_help_text
        else:
            self._help[name] = final_help_text

    def display_help(self):
        for method_name, help_text in self._help.iteritems():
            paragraphs = help_text.splitlines()
            print(paragraphs[0])
            for p in paragraphs[1:]:
                for line in self._wrapper.wrap(p):
                    print(line)
            print("")

    def run(self):
        method_name = get_method()
        if not method_name:
            if not self._default:
                print('No default method defined.')
            else:
                self._default()
            return
        if method_name == 'help':
            self.display_help()
            return
        try:
            method = self._methods[method_name]
        except KeyError:
            print("Method '" + method_name + "' doesn't exit")
            return
        arguments = get_arguments()
        if len(arguments) == 0:
            method()
        if len(arguments) == 1:
            method(arguments[0])
        if len(arguments) == 2:
            method(arguments[0], arguments[1])
