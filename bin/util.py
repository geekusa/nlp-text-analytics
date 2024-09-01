# Generic utility functions
import os
import re
import fnmatch


# originally moved from exec_anaconda.py
# Note: the following functions do NOT work with Search Head
# Pooling/shared storage.
def get_splunkhome_path():
    return os.path.normpath(os.environ['SPLUNK_HOME'])


def make_splunkhome_path(p):
    return os.path.join(get_splunkhome_path(), *p)


def get_etc_path():
    return os.environ.get('SPLUNK_ETC', os.path.join(get_splunkhome_path(), 'etc'))


def get_apps_path(bundle_path=None):
    """
    Get the full path to the 'apps' directory.

    Args:
        bundle_path: path of the search bundle that contains the 'apps' directory

    Returns:
        path to the apps directory

    """
    full_path_to_apps_dir = bundle_path if bundle_path else get_etc_path()
    return os.path.normpath(os.path.join(full_path_to_apps_dir, 'apps'))


def get_staging_area_path():
    staging_path = os.path.join('var', 'run', 'splunk', 'lookup_tmp')
    return os.path.normpath(os.path.join(get_splunkhome_path(), staging_path))


def is_valid_identifier(name):
    """Check if name is a valid identifier.

    Returns True if 'name' is a valid Python identifier. Such
    identifiers don't allow '.' or '/', so may also be used to ensure
    that name can be used as a filename without risk of directory
    traversal.
    """
    return re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', name) is not None


def match_field_globs(input_fields, requested_fields):
    """Intersect input_fields with glob expansion of requested_fields.

    Args:
        input_fields (list): the fields that are present
        requested_fields (list): the fields that are requested

    Returns:
        output_fields (list): matched field names
    """
    output_fields = []

    for f in requested_fields:
        if '*' in f:  # f contains a glob
            pat = re.compile(fnmatch.translate(f))
            matches = [
                x for x in list(input_fields) if not x.startswith('__mv_') and pat.match(x)
            ]
            if len(matches) == 0:
                output_fields.append(f)
            else:
                output_fields.extend(matches)
        else:
            output_fields.append(f)

    return output_fields


class MLSPLNotImplementedError(RuntimeError):
    """Custom ML-SPL exception to capture not implemented errors."""

    pass
