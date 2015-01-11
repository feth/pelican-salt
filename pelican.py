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


# TODO: pillardise this
PELICAN_VENV = '/var/cache/pelican_venv'
# TODO: pillardise this and make it an iterable
PELICAN_DATA_DIR = "/var/cache/blog_source"
UNIX_USER = 'pelican'


_logger = logging.getLogger('pelican_module')
__virtualname__ = 'pelican'


def _conditions():
    """Internal generator: enumerate booleans for requisites.

    Logs a message about what is going to be checked"""
    _logger.debug("Checking for git")
    try:
        # Do we really need to depend on git? Perhaps be DVCS agnostic
        from salt.modules import git
    except ImportError:
        yield False
    else:
        yield True
    _logger.debug("Checking for pelican venv installed: %s", PELICAN_VENV)
    yield os.path.isdir(PELICAN_VENV)
    _logger.debug("Checking for pelican data dir: %s ", PELICAN_DATA_DIR)
    yield os.path.isdir(PELICAN_DATA_DIR)


def __virtual__():
    """Should this module be loaded?"""
    if not all(_conditions()):
        _logger.debug("Condition failed")
        return False
    return __virtualname__


def build():
    """
    Build the pelican blog

    Calls update() before.
    """
    blog_update()

    #ensure property
    __salt__['cmd.run']('chown -R %s %s' % (UNIX_USER, PELICAN_DATA_DIR))

    # ensure 'make' will find the pelican exe
    cmd_env_path = os.environ['PATH']
    env_binpath = os.path.join(PELICAN_VENV, 'bin')
    if not env_binpath in cmd_env_path:
        cmd_env_path = '%s:%s' % (
            env_binpath,
            orig_path,
            )
    ret = __salt__['cmd.run'](
        'make html',
        user=UNIX_USER,
        cwd=PELICAN_DATA_DIR,
        env={
            'PATH': cmd_env_path,
            'PWD': PELICAN_DATA_DIR,
        }

    return "Built pelican site! {0}\n".format(ret)


def blog_update():
    """
    Updates the git checkout of the blog
    """
    return __salt__['git.pull'](PELICAN_DATA_DIR, opts='origin master')


def upgrade():
    """
    Upgrades your installation of pelican
    """
    return __salt__['pip.install']('pelican', user=UNIX_USER, bin_env=PELICAN_VENV)


def install_pelican_venv(directory):
    """
    directory must exist
    """
    #ensure property
    ret = __salt__['cmd.run']('chown -R %s %s' % (UNIX_USER, PELICAN_VENV))
    _logger.debug("Creating virtualenv in %s", directory)
    ret += __salt__['virtualenv.create'](directory, pip=True, runas=UNIX_USER)
    upgrade()
    return ret

