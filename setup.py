#!/usr/bin/env python

# Copyright (C) 2009, Aleksey Lim
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Convenient setup.py to bundle saccharin/0install to newly created .xo"""

import os
import shutil
import subprocess
from optparse import OptionParser

from sugar.activity import bundlebuilder


def call(cmd):
    if subprocess.call(cmd, shell=True) != 0:
        raise Exception('Fail to execute "%s" command' % cmd)


def fetch_saccharin():
    if os.path.exists(spath):
        # keep for moving back after failures
        shutil.move(spath, spath + '~')

    try:
        call('git clone git://git.sugarlabs.org/saccharin/mainline.git ' \
             '--branch production --depth 1 %s' % spath)
        call('git clone ' \
             'git://git.sugarlabs.org/zeroinstall-injector/mainline.git ' \
             '--branch xo --depth 1 %s' % zpath)
        shutil.move(os.path.join(zpath, 'zeroinstall'), spath)
        shutil.rmtree(zpath)
        shutil.rmtree(os.path.join(spath, '.git'))
    except Exception:
        shutil.rmtree(spath, ignore_errors=True)
        if os.path.exists(spath + '~'):
            print 'Bundle previous saccharin.'
            shutil.move(spath + '~', spath)
            return
        raise

    shutil.rmtree(spath + '~', ignore_errors=True)
    call('%s fix_manifest' % __file__)


parser = OptionParser()
parser.disable_interspersed_args()
(_, args) = parser.parse_args()

spath = os.path.join(os.path.dirname(__file__), 'saccharin')
zpath = os.path.join(spath, 'zeroinstall-injector')

if args and args[0] == 'fetch_saccharin':
    fetch_saccharin()
    exit(0)

if args and args[0] == 'dist_xo' and not os.path.islink(spath):
    fetch_saccharin()

bundlebuilder.start()
