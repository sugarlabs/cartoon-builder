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
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

import theme
from sound import Sound
from ground import Ground
from utils import *

class Document:
    tape = []
    ground = None
    sound = None

    class Tape:
        def __init__(self):
            self.clean()

        def clean(self):
            self.orig = theme.EMPTY_ORIG
            self.filename = theme.EMPTY_FILENAME

    for i in range(theme.TAPE_COUNT):
        tape.append(Tape())

def save(filepath):
    zip = Zip(filepath, 'w')
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

    saved = {}
    tape = SubElement(manifest, 'tape')
    for i in range(theme.TAPE_COUNT):
        frame = SubElement(tape, 'frame')
        if Document.tape[i].filename:
            frame.attrib['preinstalled'] = '1'
            frame.attrib['filename'] = Document.tape[i].filename
        else:
            frame.attrib['preinstalled'] = '0'
            arcname = saved.get(Document.tape[i].orig)
            if not arcname:
                arcname = saved[Document.tape[i].orig] = 'frame%03d.png' % i
                zip.write_pixbuf(arcname, Document.tape[i].orig)
            frame.attrib['filename'] = arcname

    zip.writestr('MANIFEST.xml', tostring(manifest, encoding='utf-8'))
    zip.close()

    import shutil
    shutil.copy(filepath, '/tmp/foo.zip')

def load(filepath):
    zip = Zip(filepath, 'r')
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
    for i, frame in enumerate(manifest.findall('tape/frame')):
        if i >= theme.TAPE_COUNT:
            continue
        if int(frame.attrib['preinstalled']):
            if frame.attrib['filename'] == theme.EMPTY_FILENAME:
                Document.tape[i].orig = theme.EMPTY_ORIG
            else:
                Document.tape[i].orig = theme.pixbuf(frame.attrib['filename'])
            Document.tape[i].filename = frame.attrib['filename']
        else:
            pixbuf = loaded.get(frame.attrib['filename'])
            if not pixbuf:
                pixbuf = zip.read_pixbuf(frame.attrib['filename'])
                loaded[frame.attrib['filename']] = pixbuf
            Document.tape[i].orig = pixbuf
            Document.tape[i].filename = None

    zip.close()
