# coding: utf-8
"""
    Provide saltstack building for pelican

    http://docs.saltstack.com/ref/modules/index.html#modules-are-easy-to-write

    This file:
    Copyright: 2014 Majerti
    License: Apache-2.0 http://www.apache.org/licenses/LICENSE-2.0
"""

import logging
import os
import shlex
import subprocess


from salt import exceptions


PELICAN_VENV = '/var/cache/pelican_venv'
PELICAN_DATA_DIR = "/var/cache/blog_source"


_logger = logging.getLogger('pelican_module')


def _conditions():
    """Internal generator: enumerate booleans for requisites.

    Logs a message about what is going to be checked"""
    logging.debug("Checking for git")
    try:
        from salt.modules import git
    except ImportError:
        yield False
    else:
        yield True
    logging.debug("Checking for pelican venv installed: %s", PELICAN_VENV)
    yield os.path.isdir(PELICAN_VENV)
    logging.debug("Checking for pelican data dir: %s ", PELICAN_DATA_DIR)
    yield os.path.isdir(PELICAN_DATA_DIR)


def __virtual__():
    """Should this module be loaded?"""
    if not all(_conditions()):
        logging.debug("Condition failed")
        return False
    return """pelican"""


def build():
    """
    Build the pelican blog

    Calls update() before.
    """
    blog_update()

    # PWD variable is used by the Makefile
    env = {
        'PATH': ':'.join((
            '%s/bin/' % PELICAN_VENV,
            os.environ['PATH']
            )),
        'PWD': PELICAN_DATA_DIR,
        }
    command = 'make html'
    process = subprocess.Popen(
        shlex.split(command),
        env=env,
        cwd=PELICAN_DATA_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
    process.wait() # risk of overfilling PIPEs?
    stdout_data, stderr_data = process.communicate()
    returncode = process.returncode

    if returncode == 0:
        return "pelican salt module, building %s\n%s" % (
            PELICAN_DATA_DIR,
            stdout_data
            )
    raise exceptions.CommandExecutionError('\n'.join((
        '"make html" -> ...',
        'stdout:',
        stdout_data,
        'stderr:',
        stderr_data,
        'env:',
        str(env),
        )))


def blog_update():
    """
    Updates the git checkout of the blog
    """
    return __salt__['git.pull'](PELICAN_DATA_DIR, opts='origin master')


def upgrade():
    """
    Upgrades your installation of pelican
    """
    command = "%s/bin/pip install --upgrade pelican" % PELICAN_VENV
    process = subprocess.Popen(
        shlex.split(command),
        cwd=PELICAN_DATA_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
    process.wait() # risk of overfilling PIPEs?
    stdout_data, stderr_data = process.communicate()
    returncode = process.returncode

    if returncode == 0:
        return "pelican update:\n%s" % (
            stdout_data
            )
    raise exceptions.CommandExecutionError('\n'.join((
        '"make html" -> ...',
        'stdout:',
        stdout_data,
        'stderr:',
        stderr_data,
        'env:',
        )))
