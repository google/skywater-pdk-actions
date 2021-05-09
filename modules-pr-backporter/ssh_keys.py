#!/usr/bin/env python3
# Copyright 2019-2021 SkyWater PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache 2.0

import logging
import os
import subprocess
import sys
import re
import warnings


DOT_SSH = os.path.expanduser('~/.ssh')
SSH_CONFIG = os.path.join(DOT_SSH, 'config')

SSH_KEYS = {}


class EnvironmentWarning(RuntimeWarning):
    pass


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        # Sending signal 0 to a pid will raise an OSError exception if the pid
        # is not running, and do nothing otherwise.
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def check_running():
    """ Check the SSH agent is running. """
    agent_pid = os.environ.get('SSH_AGENT_PID', '-1')
    try:
        agent_pid = int(agent_pid)
    except ValueError as e:
        warnings.warn(f"SSH_AGENT_PID was invalid {agent_pid}: {e}!", EnvironmentWarning)
        return False

    if agent_pid == -1:
        warnings.warn("SSH_AGENT_PID was not found!", EnvironmentWarning)
        return False

    if not check_pid(agent_pid):
        warnings.warn(f"SSH_AGENT_PID ({agent_pid}) was not running!", EnvironmentWarning)
        return False

    agent_sock = os.environ.get('SSH_AUTH_SOCK', '')
    if not agent_sock:
        warnings.warn("SSH_AUTH_SOCK was not found!", EnvironmentWarning)
        return False

    if not os.path.exists(agent_sock):
        warnings.warn("SSH_AUTH_SOCK (file: {agent_sock}) does not exist!", EnvironmentWarning)
        return False

    return True


def pubkey_filename(name):
    if name.startswith('/'):
        return name+'.pub'
    else:
        return os.path.join(DOT_SSH, re.sub('[^A-Za-z0-9_]', '_', name)+'.pub')


def pubkey_add_alias(name, alias):
    assert name in SSH_KEYS, (name, SSH_KEYS)
    fname, algo, pubkey = SSH_KEYS[name]
    assert os.path.exists(fname), (f'{fname} not found', name, alias, (fname, algo, pubkey))
    pubkey_add(alias, algo, pubkey)


def pubkey_add(name, algo, pubkey):
    fname = pubkey_filename(name)
    if name in SSH_KEYS:
        assert SSH_KEYS[name] == (fname, algo, pubkey), (
                name+' already exists in SSH_KEYS', SSH_KEYS[name], (fname, algo, pubkey))
        return

    if not os.path.exists(fname):
        warnings.warn(f'{fname} does not exist on file system.')
        with open(fname, 'w') as f:
            f.write(f'{algo} {pubkey} {name}\n')

    logging.debug('Found %s in file %s', name, fname)
    SSH_KEYS[name] = (fname, algo, pubkey)
    return True


def import_agent_pubkeys():
    """ Import the keys currently in the ssh-agent. """
    global SSH_KEYS

    setup_dotssh()

    p = subprocess.Popen(['ssh-add', '-L'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()
    output = p.stdout.read().decode('utf-8')
    if p.returncode != 0:
        if 'The agent has no identities.' in output:
            return []
        raise SystemError('ssh-add -L failed with:\n'+output)

    # ssh-rsa XXXXX /usr/local/google/home/tansell/.ssh/keys/new_misc_key
    # ecdsa-sha2-nistp256 XXXXXX publickey
    new_keys = []
    for l in output.splitlines():
        algo, pubkey, name = l.split(maxsplit=3)

        if pubkey_add(name, algo, pubkey):
            new_keys.append(name)

    return new_keys


def import_env_keys():
    """ Import keys from environment into the agent. """
    assert check_running(), 'ssh_agent was not running!'

    setup_dotssh()

    errors = {}
    new_keys = {}
    for k, v in os.environ.items():
        if 'PRIVATE KEY' not in v:
            continue

        if v[-1] != '\n':
            v += '\n'

        logging.debug('Importing private key in environment variable %s', k)
        p = subprocess.Popen(['ssh-add', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate(v.encode('utf-8'))
        logging.debug('ssh-add stdout\n----------------\n%s\n------------', stdout)
        logging.debug('ssh-add stderr\n----------------\n%s\n------------', stderr)
        if p.returncode != 0:
            errors[k] = (stderr, stdout)

        l = stderr.decode('utf-8').strip()
        prefix = "Identity added: (stdin) ("
        suffix = ")"
        assert l.startswith(prefix), (l, prefix)
        assert l.endswith(suffix), (l, suffix)
        keyname = l[len(prefix):-len(suffix)]
        new_keys[k] = keyname

    if errors:
        raise SystemError('Unable to import keys from {}.'.format(','.join(errors.keys())))

    import_agent_pubkeys()
    for k, v in new_keys.items():
        pubkey_add_alias(v, k)

    return list(new_keys.values())


def setup_dotssh():
    """ Make sure that ~/.ssh exists and is writable. """
    if not os.path.exists(DOT_SSH):
        logging.debug('Creating %s', DOT_SSH)
        os.makedirs(DOT_SSH)
        os.chmod(DOT_SSH, 0o700)

    with open(SSH_CONFIG, 'a+') as f:
        pass

    assert os.path.exists(SSH_CONFIG), 'Did not create a ~/.ssh/config file'


def start_agent():
    """ Start the ssh-agent. """
    assert not check_running(), 'ssh_agent was already running!'
    out = subprocess.check_output(['ssh-agent', '-c'])

    # setenv SSH_AUTH_SOCK /tmp/ssh-XXXXXXTvNg13/agent.4035507;
    # setenv SSH_AGENT_PID 4035508;
    # echo Agent pid 4035508;
    new_env = {}
    for ol in out.decode('utf-8').splitlines():
        l = ol.strip()

        p = 'setenv '
        if not l.startswith(p):
            logging.debug('Skipping ssh-agent line output of: %r', ol)
            continue
        assert l.startswith(p), repr(l)
        l = l[len(p):]

        assert l.endswith(';'), repr(l)
        l = l[:-1]

        k, v = l.split(maxsplit=1)
        assert k.startswith('SSH_'), ('Bad ssh-agent line of:', ol)
        logging.debug('Got %r=%r', k, v)
        new_env[k] = v

    for k, v in new_env.items():
        os.environ[k] = v

    if 'GITHUB_ENV' in os.environ:
        with open(os.environ['GITHUB_ENV'], "a+") as f:
            for k, v in new_env.items():
                f.write(f'{k}={v}\n')


def import_keys():
    if not check_running():
        start_agent()

    assert check_running(), "ssh_agent didn't start!?"
    import_agent_pubkeys()
    import_env_keys()


def main(args):
    logging.basicConfig(level=logging.DEBUG)

    new_keys = import_agent_pubkeys()
    print()
    print('Current agent keys:')
    for k in new_keys:
        print(k, SSH_KEYS[k])

    new_keys2 = import_agent_pubkeys()
    assert not new_keys2

    print()
    print('Environment keys:')
    env_keys = import_env_keys()
    assert env_keys, env_keys
    for k in env_keys:
        print(k, SSH_KEYS[k])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
