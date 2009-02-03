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
from zipfile import ZipFile
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

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
    manifest = Element('memorize')

    def _save(node, arcname, value):
        if value.custom():
            node.attrib['custom'] = '1'
            node.attrib['filename'] = arcname
            zip.writestr(arcname, value.read())
        else:
            node.attrib['custom'] = '0'
            node.attrib['filename'] = value.filename()
        node.text = value.name

    _save(SubElement(manifest, 'ground'), 'ground.png', Document.ground)
    _save(SubElement(manifest, 'sound'), 'sound', Document.sound)

    arcfiles = {}
    for i, frame in enumerate(
            [i for i in set(Document.tape) if not i.empty() and i.custom()]):
        arcfiles[frame] = 'frame%03d.png' % i
        zip.writestr(arcfiles[frame], frame.read())

    tape = SubElement(manifest, 'tape')
    for i, frame in enumerate(Document.tape):
        if frame.empty():
            continue
        node = SubElement(tape, 'frame')
        if frame.custom():
            node.attrib['custom'] = '1'
            node.attrib['filename'] = arcfiles[frame]
        else:
            node.attrib['custom'] = '0'
            node.attrib['filename'] = frame.filename()
        node.attrib['index'] = str(i)

    zip.writestr('MANIFEST.xml', tostring(manifest, encoding='utf-8'))
    zip.close()

    import shutil
    shutil.copy(filepath, '/tmp/foo.zip')

def load(filepath):
    zip = ZipFile(filepath, 'r')
    manifest = fromstring(zip.read('MANIFEST.xml'))

    def _load(node, klass):
        if int(node.attrib['custom']):
            out = klass(node.text, zip.read(node.attrib['filename']),
                    theme.RESTORED)
        else:
            out = klass(node.text, node.attrib['filename'], theme.PREINSTALLED)
        return out

    Document.ground = _load(manifest.find('ground'), Ground)
    Document.sound = _load(manifest.find('sound'), Sound)

    loaded = {}
    for node in manifest.findall('tape/frame'):
        i = int(node.attrib['index'])
        if i >= theme.TAPE_COUNT:
            continue
        filename = node.attrib['filename']
        if int(node.attrib['custom']):
            frame = loaded.get(filename)
            if not frame:
                frame = loaded[filename] = Frame(
                        zip.read(filename), theme.RESTORED)
            Document.tape[i] = frame
        else:
            Document.tape[i] = Frame(filename, theme.PREINSTALLED)

    zip.close()
