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
from utils import pixbuf, pixbuf2str

def load():
    from document import Document

    custom = THEMES[-1]
    for i, f in enumerate(
            [i for i in set(Document.tape) if not i.empty() and i.custom()]):
        custom.frames[i] = f

class Frame:
    def __init__(self, image, type):
        self._type =  type
        self._thumb = None
        self._orig = None
        self._filename = None

        if type == theme.RESTORED:
            tmpfile = os.path.join(theme.SESSION_PATH, '.tmp.png')
            file(tmpfile, 'w').write(image)
            self._orig = theme.pixbuf(tmpfile)
            os.unlink(tmpfile)
        elif type == theme.CUSTOM:
            self._thumb = theme.CUSTOM_FRAME_THUMB
        elif type == theme.EMPTY:
            self._type = theme.PREINSTALLED
            self._thumb = theme.EMPTY_THUMB
            self._orig = theme.EMPTY_ORIG
        else:
            self._filename = image

    def read(self):
        if not self._orig:
            return ''
        else:
            return pixbuf2str(self._orig)

    def empty(self):
        return self._thumb == theme.EMPTY_THUMB

    def custom(self):
        return self._type != theme.PREINSTALLED

    def thumb(self):
        if self._thumb == None:
            self._thumb = theme.scale(self.orig())
        return self._thumb

    def orig(self):
        if self._orig == None:
            if self._type != theme.PREINSTALLED:
                return theme.EMPTY_ORIG
            self._orig = theme.pixbuf(self._filename)
        return self._orig

    def select(self):
        if self._type != theme.CUSTOM or self._orig:
            return True;
        self._orig = theme.choose(lambda t, file: theme.pixbuf(file))
        self._thumb = theme.scale(self.orig())
        return self._orig != None

    def filename(self):
        return self._filename

class Char:
    def __init__(self, name, thumbfile, dir):
        self.name = name
        self.frames = []

        if dir:
            for i in sorted(glob.glob(theme.path(dir, '*'))):
                self.frames.append(Frame(
                        os.path.join(dir, os.path.basename(i)),
                        theme.PREINSTALLED))
            for i in range(len(self.frames)-1,
                    theme.FRAME_ROWS*theme.FRAME_COLS):
                self.frames.append(Frame(None, theme.EMPTY))
            self._thumb = theme.pixbuf(thumbfile, theme.THUMB_SIZE)
        else:
            for i in range(0, theme.FRAME_ROWS*theme.FRAME_COLS):
                self.frames.append(Frame(None, theme.CUSTOM))
            self._thumb = theme.CUSTOM_FRAME_THUMB

    def thumb(self):
        return self._thumb

    def clean(self, index):
        if self.frames[index].custom():
            self.frames[index] = Frame(None, theme.CUSTOM)

THEMES = (
    Char(_('Elephant'),     'images/pics/Elephant/bigelephant0.gif',
                            'images/pics/Elephant'),
    Char(_('Space Blob'),   'images/pics/SpaceBlob/bigblob8.gif',
                            'images/pics/SpaceBlob'),
    Char(_('Turkey'),       'images/pics/Turkey/bigturkey1.gif',
                            'images/pics/Turkey'),
    None,
    Char(_('Custom'),       None, None))
