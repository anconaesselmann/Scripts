import json


def read_options(options_path):
    options = {}
    try:
        read_file = open(options_path)
        with read_file as infile:
            options = json.load(infile)
        read_file.close()
    except:
        ()
    return options


def write_options(options_path, options):
    write_file = open(options_path, 'w')
    with write_file as outfile:
        json.dump(options, outfile)
    write_file.close()
