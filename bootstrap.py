"""
Description: Idempotent script to set up a .plist file for running the Wunderjinx queue consumer
Author: mieubrisse

TODO This still needs to create the necessary RabbitMQ queue
"""
 
import sys
import argparse
import os
import jinja2
 
_PYTHON_ENV_DIRPATH_ARGVAR = "python_environment_dirpath"
_LOG_FILEPATH_ARGVAR = "log_filepath"

_PYTHON_ENV_SITE_PACKAGES_DIRPATH = os.path.join("lib", "python2.7", "site-packages")
_PYTHON_ENV_BINARY_FILEPATH = os.path.join("bin/python")

_LAUNCH_AGENTS_DIRPATH = os.path.realpath(os.path.expanduser("~/Library/LaunchAgents"))
_PLIST_TEMPLATE_FILENAME = "queue_consumer.plist.jinja"
_PLIST_FILENAME = _PLIST_TEMPLATE_FILENAME.strip(".jinja")
_QUEUE_CONSUMER_FILENAME = "queue_consumer.py"
 
def _parse_args(argv):
    """ Parses args into a dict of ARGVAR=value, or None if the argument wasn't supplied """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(_PYTHON_ENV_DIRPATH_ARGVAR, metavar="<Python environment>", help="Python environment to use when running Wunderjinx")
    parser.add_argument(_LOG_FILEPATH_ARGVAR, metavar="<log file>", help="Log file that Wunderjinx should write to (useful for debugging errors)")
    return vars(parser.parse_args(argv))
 
def _print_error(msg):
    sys.stderr.write('Error: ' + msg + '\n')
 
def _validate_args(args):
    """ Performs validation on the given args dict, returning a non-zero exit code if errors were found or None if all is well """
    python_env_dirpath = os.path.realpath(os.path.expanduser(args[_PYTHON_ENV_DIRPATH_ARGVAR]))
    if not os.path.isdir(python_env_dirpath):
        _print_error("No Python environment directory found: " + python_env_dirpath)
        return 1
    site_packages_dirpath = os.path.join(python_env_dirpath, _PYTHON_ENV_SITE_PACKAGES_DIRPATH)
    if not os.path.isdir(site_packages_dirpath):
        _print_error("No site packages directory found: " + site_packages_dirpath)
        return 2
    python_binary_filepath = os.path.join(python_env_dirpath, _PYTHON_ENV_BINARY_FILEPATH)
    if not os.path.isfile(python_binary_filepath):
        _print_error("No Python binary found: " + python_binary_filepath)
        return 3
    return None
 
def main(argv):
    args = _parse_args(map(str, argv))
    err_code = _validate_args(args)
    if err_code is not None:
        return err_code

    python_env_dirpath = os.path.realpath(os.path.expanduser(args[_PYTHON_ENV_DIRPATH_ARGVAR]))
    log_filepath = os.path.realpath(os.path.expanduser(args[_LOG_FILEPATH_ARGVAR]))
 
    script_dirpath = os.path.dirname(os.path.realpath(os.path.expanduser(__file__)))

    queue_consumer_filepath = os.path.join(script_dirpath, "wunderjinx", "queue_consumer.py")

    plist_template_filepath = os.path.join(script_dirpath, _PLIST_TEMPLATE_FILENAME)
    with open(plist_template_filepath) as plist_template_fp:
        template_contents = plist_template_fp.read()
    template = jinja2.Template(template_contents)

    # TODO Fill in these variables with actual values!
    rendered_template = template.render(
            pythonpath=os.path.join(python_env_dirpath, _PYTHON_ENV_SITE_PACKAGES_DIRPATH),
            python_binary_filepath=os.path.join(python_env_dirpath, _PYTHON_ENV_BINARY_FILEPATH),
            queue_consumer_filepath=queue_consumer_filepath,
            log_filepath=log_filepath
            )
    print rendered_template

    with open(os.path.join(_LAUNCH_AGENTS_DIRPATH, _PLIST_FILENAME)) as output_fp:
        output_fp.write(rendered_template)
 
    return 0
 
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
