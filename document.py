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

import os
import gtk
import cjson
from zipfile import ZipFile

import theme
from sound import Sound
from ground import Ground
from utils import *

from char import Frame

class Document:
    tape = []
    ground = None
    sound = None


    for i in range(theme.TAPE_COUNT):
        tape.append(Frame(None, theme.EMPTY))

def clean(index):
    from char import Frame
    Document.tape[index] = Frame(None, theme.EMPTY)

def save(filepath):
    zip = ZipFile(filepath, 'w')

    cfg = { 'ground': {},
            'sound' : {},
            'tape'  : [] }

    def _save(node, arcname, value):
        if value.custom():
            node['custom'] = True
            node['filename'] = arcname
            zip.writestr(arcname, value.read())
        else:
            node['custom'] = False
            node['filename'] = value.filename()
        node['name'] = value.name

    _save(cfg['ground'], 'ground.png', Document.ground)
    _save(cfg['sound'], 'sound', Document.sound)

    arcfiles = {}
    for i, frame in enumerate(
            [i for i in set(Document.tape) if not i.empty() and i.custom()]):
        arcfiles[frame] = 'frame%03d.png' % i
        zip.writestr(arcfiles[frame], frame.read())

    for i, frame in enumerate(Document.tape):
        if frame.empty():
            continue
        node = {}
        if frame.custom():
            node['custom'] = True
            node['filename'] = arcfiles[frame]
        else:
            node['custom'] = False
            node['filename'] = frame.filename()
        node['index'] = i
        cfg['tape'].append(node)

    zip.writestr('MANIFEST', cjson.encode(cfg))
    zip.close()

    import shutil
    shutil.copy(filepath, '/tmp/foo.zip')

def load(filepath):
    zip = ZipFile(filepath, 'r')
    cfg = cjson.decode(zip.read('MANIFEST'))

    def _load(node, klass):
        if node['custom']:
            out = klass(node['name'], zip.read(node['filename']),
                    theme.RESTORED)
        else:
            out = klass(node['name'], node['filename'], theme.PREINSTALLED)
        return out

    Document.ground = _load(cfg['ground'], Ground)
    Document.sound = _load(cfg['sound'], Sound)

    loaded = {}
    for node in cfg['tape']:
        i = node['index']
        if i >= theme.TAPE_COUNT:
            continue
        filename = node['filename']
        if node['custom']:
            frame = loaded.get(filename)
            if not frame:
                frame = loaded[filename] = Frame(
                        zip.read(filename), theme.RESTORED)
            Document.tape[i] = frame
        else:
            Document.tape[i] = Frame(filename, theme.PREINSTALLED)

    zip.close()
