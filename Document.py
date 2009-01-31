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

import Theme
import Utils

class Document:
    tape = []

    ground_name = None
    ground_orig = None
    ground_filename = None

    sound_name = None
    sound_filename = None

    class Tape:
        def __init__(self):
            self.clean()

        def clean(self):
            self.orig = Theme.EMPTY_ORIG
            self.filename = Theme.EMPTY_FILENAME

    for i in range(Theme.TAPE_COUNT):
        tape.append(Tape())

def save(filepath):
    zip = Utils.Zip(filepath, 'w')
    manifest = Element('memorize')

    ground = SubElement(manifest, 'ground')
    if Document.ground_filename:
        ground.attrib['preinstalled'] = '1'
        ground.attrib['filename'] = Document.ground_filename
    else:
        ground.attrib['preinstalled'] = '0'
        ground.attrib['filename'] = 'ground.png'
        zip.write_pixbuf('ground.png', Document.ground_orig)
    ground.text = Document.ground_name

    sound = SubElement(manifest, 'sound')
    if not os.path.isabs(Document.sound_filename):
        sound.attrib['preinstalled'] = '1'
        sound.attrib['filename'] = Document.sound_filename
    else:
        sound.attrib['preinstalled'] = '0'
        sound.attrib['filename'] = 'sound'
        zip.write(Document.sound_filename, 'sound')
    sound.text = Document.sound_name
    
    saved = {}
    tape = SubElement(manifest, 'tape')
    for i in range(Theme.TAPE_COUNT):
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
    zip = Utils.Zip(filepath, 'r')
    manifest = fromstring(zip.read('MANIFEST.xml'))

    ground = manifest.find('ground')
    if int(ground.attrib['preinstalled']):
        Document.ground_orig = Theme.pixbuf(ground.attrib['filename'])
        Document.ground_filename = ground.attrib['filename']
    else:
        Document.ground_orig = zip.read_pixbuf(ground.attrib['filename'])
    Document.ground_name = ground.text

    sound = manifest.find('sound')
    if int(sound.attrib['preinstalled']):
        Document.sound_filename = sound.attrib['filename']
    else:
        arcfile = sound.attrib['filename']
        sndfile = os.path.join(Theme.SESSION_PATH, 'sound.001')
        file(sndfile, 'w').write(zip.read(arcfile))
        Document.sound_filename = sndfile
    Document.sound_name = sound.text

    loaded = {}
    for i, frame in enumerate(manifest.findall('tape/frame')):
        if i >= Theme.TAPE_COUNT:
            continue
        if int(frame.attrib['preinstalled']):
            Document.tape[i].orig = Theme.pixbuf(frame.attrib['filename'])
            Document.tape[i].filename = frame.attrib['filename']
        else:
            pixbuf = loaded.get(frame.attrib['filename'])
            if not pixbuf:
                pixbuf = zip.read_pixbuf(frame.attrib['filename'])
                loaded[frame.attrib['filename']] = pixbuf
            Document.tape[i].orig = pixbuf
            Document.tape[i].filename = None

    zip.close()
