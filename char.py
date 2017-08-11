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

import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import glob
from gettext import gettext as _

import toolkit.chooser as chooser
from toolkit import pixbuf

import theme


def load():
    from document import Document

    custom = THEMES[-1]
    for i, f in enumerate(
            [i for i in set(Document.tape) if not i.empty() and i.custom()]):
        custom.frames[i] = f


class Frame:
    def __init__(self, id):
        self.id = id
        self.name = ''
        self._thumb = None
        self._orig = None

    def serialize(self):
        if self._orig:
            return pixbuf.to_str(self._orig)
        else:
            return ''

    def empty(self):
        return False

    def custom(self):
        return True

    def thumb(self):
        if self._thumb == None:
            self._thumb = theme.scale(self.orig())
        return self._thumb

    def orig(self):
        return self._orig

    def select(self):
        return True


class PreinstalledFrame(Frame):
    def __init__(self, filename):
        Frame.__init__(self, filename)
        self._filename = filename

    def custom(self):
        return False

    def orig(self):
        if self._orig == None:
            self._orig = theme.pixbuf(self._filename)
        return self._orig


class EmptyFrame(Frame):
    def __init__(self):
        Frame.__init__(self, None)
        self._thumb = theme.EMPTY_THUMB
        self._orig = theme.EMPTY_ORIG

    def custom(self):
        return False

    def empty(self):
        return True;


class RestoredFrame(Frame):
    def __init__(self, id, data):
        Frame.__init__(self, id)
        self._orig = pixbuf.from_str(data)


class CustomFrame(Frame):
    def __init__(self):
        Frame.__init__(self, None)
        self._thumb = theme.CUSTOM_FRAME_THUMB

    def orig(self):
        if self._orig == None:
            return theme.EMPTY_ORIG
        return self._orig

    def select(self):
        if self._orig:
            return True;
        self.name, self.id, self._orig = chooser.pick(
                lambda jobject: (jobject.metadata['title'], jobject.object_id,
                        theme.pixbuf(jobject.file_path)),
                (None, None, None), what=chooser.IMAGE)
        if self.name:
            self._thumb = theme.scale(self._orig)
            return True
        else:
            return False


class Char:
    def __init__(self, name, thumbfile, dir):
        self.name = name
        self.frames = []

        if dir:
            for i in sorted(glob.glob(theme.path(dir, '*'))):
                self.frames.append(PreinstalledFrame(
                        os.path.join(dir, os.path.basename(i))))
            self._thumb = theme.pixbuf(thumbfile, theme.THUMB_SIZE)
            self._custom = False
        else:
            for i in range(0, theme.FRAME_ROWS * theme.FRAME_COLS):
                self.frames.append(CustomFrame())
            self._thumb = theme.CUSTOM_FRAME_THUMB
            self._custom = True

    def custom(self):
        return self._custom

    def thumb(self):
        return self._thumb

    def clean(self, index):
        if self.frames[index].custom():
            self.frames[index] = CustomFrame()

THEMES = (
    Char(_('Elephant'),     'images/pics/Elephant/bigelephant0.gif',
                            'images/pics/Elephant'),
    Char(_('Space Blob'),   'images/pics/SpaceBlob/bigblob8.gif',
                            'images/pics/SpaceBlob'),
    Char(_('Turkey'),       'images/pics/Turkey/bigturkey1.gif',
                            'images/pics/Turkey'),
    None,
    Char(_('Custom'),       None, None))
