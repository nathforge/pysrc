#!/usr/bin/python

import imp
import os
import stat
import subprocess
import sys
import tempfile

def get_module_path(module_name):
    for path in sys.path:
        segments = module_name.split('.')
        for i, segment in enumerate(segments):
            last_segment = (i == len(segments) - 1)
            segment_path = os.path.join(path, *segments[:i])
            try:
                module_file, pathname, (suffix, mode, module_type) = \
                    imp.find_module(segment, [segment_path])
            except ImportError:
                break
            else:
                if last_segment:
                    if module_type == imp.PKG_DIRECTORY:
                        pathname = os.path.join(pathname, '__init__.py')
                    return pathname

def get_module_source_from_hooks(module_name):
    for path in sys.path:
        for path_hook in sys.path_hooks:
            try:
                importer = path_hook(path)
            except ImportError:
                pass
            else:
                try:
                    return importer.get_source(module_name)
                except ImportError:
                    pass

if __name__ == '__main__':
    from optparse import OptionParser, Option
    
    parser = OptionParser(usage='%prog module [options]', option_list=(
        Option('-e', '--editor', default=os.environ.get('PYSRC_EDITOR'),
            help='Editor executable. Defaults to $PYSRC_EDITOR'),
    ))
    options, args = parser.parse_args()
    
    if len(args) < 1:
        parser.error('No module given')
    elif len(args) > 1:
        parser.error('Too many arguments')
    
    module_name = args[0]
    
    if not options.editor:
        parser.error('Please set $PYSRC_EDITOR in your environment, or '
                     'use the --editor option')
    
    module_path = get_module_path(module_name)
    temp_file = None
    if module_path is None:
        module_source = get_module_source_from_hooks(module_name)
        if module_source:
            temp_file, module_path = tempfile.mkstemp('.py')
            os.chmod(module_path, stat.S_IREAD)
            os.fdopen(temp_file, 'wb').write(module_source)
    
    if not module_path:
        parser.error('Can\'t find source for "%s"' % module_name)
    
    subprocess.call([options.editor, module_path])

