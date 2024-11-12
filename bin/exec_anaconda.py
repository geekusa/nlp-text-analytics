# Copyright (C) 2015-2019 Splunk Inc. All Rights Reserved.

# To be used in accordance with the README file in Python for Scientific
# Computing (PSC). That is, exec_anaconda.py is available to be copied and
# placed into your applications as needed to allow for the execution of Splunk
# Custom Search Commands and cross-platform module imports. See the PSC README
# file for more details.
import json
import os
import platform
import stat
import subprocess
import sys
import time
import traceback

from util import get_apps_path

# NOTE: This file must be Python 2 and 3 compatible until
# Splunk Enterprise drops support for Python2.

# Prefix of the directory name where PSC is installed
PSC_PATH_PREFIX = 'Splunk_SA_Scientific_Python_'

SUPPORTED_SYSTEMS = {
    ('Linux', 'x86_64'): 'linux_x86_64',
    ('Darwin', 'x86_64'): 'darwin_x86_64',
    ('Darwin', 'arm64'): 'darwin_arm64',
    ('Windows', 'AMD64'): 'windows_x86_64',
}


def check_python_version():
    if sys.version_info[0] < 3:
        raise Exception(
            'This version of MLTK must be run under Python3. Please consult MLTK documentation for more information'
        )


def exec_anaconda():
    """Re-execute the current Python script using the Anaconda Python
    interpreter included with Splunk_SA_Scientific_Python.

    After executing this function, you can safely import the Python
    libraries included in Splunk_SA_Scientific_Python (e.g. numpy).

    Canonical usage is to put the following at the *top* of your
    Python script (before any other imports):

       import exec_anaconda
       exec_anaconda.exec_anaconda()

       # Your other imports should now work.
       import numpy as np
       import pandas as pd
       ...
    """
    if PSC_PATH_PREFIX in sys.executable:
        from imp import reload

        fix_sys_path()

        reload(json)
        reload(os)
        reload(platform)
        reload(stat)
        reload(subprocess)
        reload(sys)
        return

    check_python_version()

    sa_path, system = get_system_paths()

    system_path = os.path.join(sa_path, 'bin', '%s' % (SUPPORTED_SYSTEMS[system]))

    if system[0] == 'Windows':
        python_path = os.path.join(system_path, 'python.exe')
        # MLA-564: Windows need the DLLs to be in the PATH
        dllpath = os.path.join(system_path, 'Library', 'bin')
        pathsep = os.pathsep if 'PATH' in os.environ else ''
        os.environ['PATH'] = os.environ.get('PATH', '') + pathsep + dllpath
    else:
        python_path = os.path.join(system_path, 'bin', 'python')

    # MLA-996: Unset PYTHONHOME
    # XXX: After migration to Python3 PYTHONPATH is not set anymore so this will
    # be unnecessary. SPL-170875
    os.environ.pop('PYTHONHOME', None)

    # Ensure that execute bit is set on <system_path>/bin/python
    if system[0] != 'Windows':
        mode = os.stat(python_path).st_mode
        os.chmod(python_path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    sys.stderr.flush()

    # In Quake and later PYTHONPATH is removed or not set.
    # So after shelling into PSC Python interpreter will lose
    # information about what Splunk core's Python path is. So we
    # stash it into an environment variable to retrieve it after
    # switching into conda.
    os.environ['SPLUNK_CORE_PYTHONPATH'] = json.dumps(sys.path)

    try:
        os.environ['MKL_NUM_THREADS'] = '4'
        if system[0] == "Windows":
            # os.exec* broken on Windows: http://bugs.python.org/issue19066
            subprocess.check_call([python_path] + sys.argv)
            os._exit(0)
        else:
            os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
            os.environ['OPENBLAS_NUM_THREADS'] = '4'
            os.execl(python_path, python_path, *sys.argv)
    except Exception:
        traceback.print_exc(None, sys.stderr)
        sys.stderr.flush()
        time.sleep(0.1)
        raise RuntimeError(
            'Error encountered while loading Python for Scientific Computing, see search.log.'
        )


def fix_sys_path():
    # After shelling into PSC's Python interpreter, we no longer have access
    # to Splunk core's Python path to import stuff from there. So we retrieve
    # that path from the environment variable we set before.
    splunk_python_path = os.environ.get('SPLUNK_CORE_PYTHONPATH')
    if not splunk_python_path:
        raise Exception('Can not find Splunk core Python path')
    try:
        splunk_python_path = json.loads(splunk_python_path)
    except Exception as e:
        raise Exception('Can not parse Splunk core Python path: %r' % e)
    for item in splunk_python_path:
        if item not in sys.path:
            sys.path.append(item)

    # XXX: Since PYTHONPATH is gone in Splunk 8 onwards
    # the following block will have no effect, but will
    # keep it for now. SPL-170875
    # Update sys.path to move Splunk's PYTHONPATH to the end. We want
    # to import Anaconda's built-ins before Splunk's.
    pp = os.environ.get('PYTHONPATH')
    if not pp:
        return
    for spp in pp.split(os.pathsep):
        try:
            sys.path.remove(spp)
            sys.path.append(spp)
        except Exception:
            pass

    # MLA-2136: update environment variable such that subprocesses
    # (from watchdog) will also have Anaconda's builtins available before
    # Splunk's builtins.
    if platform.system() == 'Windows':
        os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)


def exec_anaconda_or_die():
    try:
        exec_anaconda()
    except Exception as e:
        print('Failed to activate Conda environment: %r' % e, sys.stderr)
        import cexc

        cexc.abort(e)
        sys.exit(1)

def get_system_paths():
    if platform.system() == "Darwin" and "ARM64" in platform.version():
        system = (platform.system(), "arm64")
    else:
        system = (platform.system(), platform.machine())
    if system not in SUPPORTED_SYSTEMS:
        raise Exception(f'Unsupported platform: {system}')

    sa_scipy = f"{PSC_PATH_PREFIX}{SUPPORTED_SYSTEMS[system]}"

    sa_path = os.path.join(get_apps_path(), sa_scipy)

    if not os.path.isdir(sa_path):
        raise Exception(f'Failed to find Python for Scientific Computing Add-on ({sa_scipy})')

    return sa_path, system