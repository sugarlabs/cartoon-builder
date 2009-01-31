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

import gtk
from gettext import gettext as _

from sugar.graphics.objectchooser import ObjectChooser

import Theme
from Document import Document

PREINSTALLED = 0
CUSTOM       = 1
TEMPORARY    = 2

def load():
    if not Document.ground_filename:
        custom = Ground(Document.ground_name, None, TEMPORARY)
        custom._pixbuf = Document.ground_orig
        THEMES.insert(-1, custom)

class Ground:
    def __init__(self, name, file, type):
        self.name = name
        self._file = file
        if file: self._pixbuf = Theme.pixbuf(file)
        self._type = type
        self._thumb = None

    def filename(self):
        if self._type == PREINSTALLED:
            return self._file
        else:
            return None

    def thumb(self):
        if not self._thumb:
            self._thumb = Theme.scale(self._pixbuf)
        return self._thumb

    def orig(self):
        return self._pixbuf

    def change(self):
        if self._type != CUSTOM:
            return self
        return Theme.choose(lambda title, file: Ground(title, file, TEMPORARY))

THEMES = [
    Ground(_('Saturn'),     'images/backpics/bigbg01.gif', PREINSTALLED),
    Ground(_('Snowflakes'), 'images/backpics/bigbg02.gif', PREINSTALLED),
    Ground(_('Eye'),        'images/backpics/bigbg03.gif', PREINSTALLED),
    Ground(_('Blobs'),      'images/backpics/bigbg04.gif', PREINSTALLED),
    Ground(_('Star Night'), 'images/backpics/bigbg05.gif', PREINSTALLED),
    Ground(_('Forest'),     'images/backpics/bigbg06.gif', PREINSTALLED),
    Ground(_('Spiral'),     'images/backpics/bigbg07.gif', PREINSTALLED),
    Ground(_('Beam'),       'images/backpics/bigbg08.gif', PREINSTALLED),
    Ground(_('Cloth'),      'images/backpics/bigbg09.gif', PREINSTALLED),
    Ground(_('Faces'),      'images/backpics/bigbg10.gif', PREINSTALLED),
    Ground(_('Leaves'),     'images/backpics/bigbg11.gif', PREINSTALLED),
    Ground(_('Vegetables'), 'images/backpics/bigbg12.gif', PREINSTALLED),
    Ground(_('Spotlight'),  'images/backpics/bigbg13.gif', PREINSTALLED),
    Ground(_('Strips'),     'images/backpics/bigbg14.gif', PREINSTALLED),
    Ground(_('Scene'),      'images/backpics/bigbg15.gif', PREINSTALLED),
    Ground(_('Rhombs'),     'images/backpics/bigbg16.gif', PREINSTALLED),
    Ground(_('Milky Way'),  'images/backpics/bigbg17.gif', PREINSTALLED),
    None,
    Ground(_('Custom'),     'images/backpics/custom.png', CUSTOM)]
