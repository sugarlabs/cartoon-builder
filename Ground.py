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

def load():
    ground = Document.ground()
    custom = Ground(ground[0], None, False)
    custom._pixbuf = ground[1]
    THEMES.insert(-1, custom)

class Ground:
    def __init__(self, name, file, custom):
        self.name = name
        if file: self._pixbuf = Theme.pixbuf(file)
        self._custom = custom
        self._thumb = None

    def thumb(self):
        if not self._thumb:
            self._thumb = Theme.scale(self._pixbuf)
        return self._thumb

    def orig(self):
        return self._pixbuf

    def change(self):
        if self._custom in (None, False):
            return self
        else:
            return Theme.choose(lambda title, file: Ground(title, file, False))

THEMES = (
    Ground(_('Saturn'),     'images/backpics/bigbg01.gif', None),
    Ground(_('Snowflakes'), 'images/backpics/bigbg02.gif', None),
    Ground(_('Eye'),        'images/backpics/bigbg03.gif', None),
    Ground(_('Blobs'),      'images/backpics/bigbg04.gif', None),
    Ground(_('Star Night'), 'images/backpics/bigbg05.gif', None),
    Ground(_('Forest'),     'images/backpics/bigbg06.gif', None),
    Ground(_('Spiral'),     'images/backpics/bigbg07.gif', None),
    Ground(_('Beam'),       'images/backpics/bigbg08.gif', None),
    Ground(_('Cloth'),      'images/backpics/bigbg09.gif', None),
    Ground(_('Faces'),      'images/backpics/bigbg10.gif', None),
    Ground(_('Leaves'),     'images/backpics/bigbg11.gif', None),
    Ground(_('Vegetables'), 'images/backpics/bigbg12.gif', None),
    Ground(_('Spotlight'),  'images/backpics/bigbg13.gif', None),
    Ground(_('Strips'),     'images/backpics/bigbg14.gif', None),
    Ground(_('Scene'),      'images/backpics/bigbg15.gif', None),
    Ground(_('Rhombs'),     'images/backpics/bigbg16.gif', None),
    Ground(_('Milky Way'),  'images/backpics/bigbg17.gif', None),
    None,
    Ground(_('Custom'),     'images/backpics/custom.png', True) )
