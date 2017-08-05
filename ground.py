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
gi.require_version('Gtk', '3.0')
import os
from gi.repository import Gtk
from gettext import gettext as _

import toolkit.chooser as chooser
from toolkit import pixbuf

import theme


def load():
    from document import Document

    if Document.ground and Document.ground.custom():
        THEMES.append(Document.ground)


class Ground:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self._thumb = None

    def custom(self):
        return True

    def serialize(self):
        return pixbuf.to_str(self._orig)

    def thumb(self):
        if not self._thumb:
            self._thumb = theme.scale(self._orig)
        return self._thumb

    def orig(self):
        return self._orig

    def select(self):
        return self


class PreinstalledGround(Ground):
    def __init__(self, name, filename):
        Ground.__init__(self, name, filename)
        self._orig = theme.pixbuf(filename)

    def custom(self):
        return False


class CustomGround(Ground):
    def __init__(self, name, filename):
        Ground.__init__(self, name, None)
        self._orig = theme.pixbuf(filename)

    def select(self):
        try:
            return chooser.pick(lambda jobject: JournalGround(jobject),
                    what=chooser.IMAGE)
        except:
            return None


class RestoredGround(Ground):
    def __init__(self, name, id, data):
        Ground.__init__(self, name, id)
        self._orig = pixbuf.from_str(data)


class JournalGround(Ground):
    def __init__(self, jobject):
        Ground.__init__(self, jobject.metadata['title'], jobject.object_id)
        self._orig = theme.pixbuf(jobject.file_path)
        THEMES.append(self)

THEMES = [
    PreinstalledGround(_('Saturn'),     'images/backpics/bigbg01.gif'),
    PreinstalledGround(_('Snowflakes'), 'images/backpics/bigbg02.gif'),
    PreinstalledGround(_('Eye'),        'images/backpics/bigbg03.gif'),
    PreinstalledGround(_('Blobs'),      'images/backpics/bigbg04.gif'),
    PreinstalledGround(_('Star Night'), 'images/backpics/bigbg05.gif'),
    PreinstalledGround(_('Forest'),     'images/backpics/bigbg06.gif'),
    PreinstalledGround(_('Spiral'),     'images/backpics/bigbg07.gif'),
    PreinstalledGround(_('Beam'),       'images/backpics/bigbg08.gif'),
    PreinstalledGround(_('Cloth'),      'images/backpics/bigbg09.gif'),
    PreinstalledGround(_('Faces'),      'images/backpics/bigbg10.gif'),
    PreinstalledGround(_('Leaves'),     'images/backpics/bigbg11.gif'),
    PreinstalledGround(_('Vegetables'), 'images/backpics/bigbg12.gif'),
    PreinstalledGround(_('Spotlight'),  'images/backpics/bigbg13.gif'),
    PreinstalledGround(_('Strips'),     'images/backpics/bigbg14.gif'),
    PreinstalledGround(_('Scene'),      'images/backpics/bigbg15.gif'),
    PreinstalledGround(_('Rhombs'),     'images/backpics/bigbg16.gif'),
    PreinstalledGround(_('Milky Way'),  'images/backpics/bigbg17.gif'),
    None,
    CustomGround(_('Custom'), 'images/backpics/custom.png')]
