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
import glob
from gettext import gettext as _

import theme
from document import Document

PREINSTALLED = 0
CUSTOM       = 1

def load():
    custom = THEMES[-1]

    index = 0
    loaded = {}
    for i in range(theme.TAPE_COUNT):
        orig = Document.tape[i].orig
        if Document.tape[i].filename or loaded.has_key(orig):
            continue
        loaded[orig] = True
        custom._origs[index] = orig
        custom._thumbs[index] = theme.scale(orig)
        index += 1

class Char:
    def __init__(self, name, file, dir, type):
        self.name = name
        self._thumb = theme.pixbuf(file, theme.THUMB_SIZE)
        self._type = type
        self._thumbs = {}
        self._origs = {}
        self._filenames = []

        if type != CUSTOM:
            for i in sorted(glob.glob(theme.path(dir, '*'))):
                self._filenames.append(os.path.join(dir, os.path.basename(i)))

    def filename(self, index):
        if self._type == CUSTOM:
            return None
        elif index >= len(self._filenames):
            return theme.EMPTY_FILENAME
        else:
            return self._filenames[index]

    def thumb(self, index = None):
        if index == None:
            return self._thumb

        pix = self._thumbs.get(index)

        if pix == None:
            if self._type == CUSTOM:
                pix = self._thumb
            else:
                if index < len(self._filenames):
                    pix = theme.pixbuf(self._filenames[index], theme.THUMB_SIZE)
                else:
                    pix = theme.EMPTY_THUMB
            self._thumbs[index] = pix

        return pix

    def orig(self, index):
        pix = self._origs.get(index)

        if pix == None:
            if self._type == CUSTOM:
                pix = theme.choose(lambda t, file: theme.pixbuf(file))
                if pix:
                    self._thumbs[index] = theme.scale(pix)
                    self._origs[index] = pix
            else:
                if index < len(self._filenames):
                    pix = theme.pixbuf(self._filenames[index])
                    self._origs[index] = pix
                else:
                    pix = theme.EMPTY_ORIG

        return pix

    def clean(self, index):
        if self._type != CUSTOM:
            return
        if self._thumbs.has_key(index):
            del self._thumbs[index]
        if self._origs.has_key(index):
            del self._origs[index]

THEMES = (
    Char(_('Elephant'),     'images/pics/Elephant/bigelephant0.gif',
                            'images/pics/Elephant', PREINSTALLED),
    Char(_('Space Blob'),   'images/pics/SpaceBlob/bigblob8.gif',
                            'images/pics/SpaceBlob', PREINSTALLED),
    Char(_('Turkey'),       'images/pics/Turkey/bigturkey1.gif',
                            'images/pics/Turkey', PREINSTALLED),
    None,
    Char(_('Custom'),       'images/pics/custom.png', None, CUSTOM))
