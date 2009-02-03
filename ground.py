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
from gettext import gettext as _

from sugar.graphics.objectchooser import ObjectChooser

import theme
from utils import pixbuf, pixbuf2str

def load():
    from document import Document

    if Document.ground and Document.ground.custom():
        THEMES.insert(-1, Document.ground)

class Ground:
    def __init__(self, name, image, type):
        self.name = name
        self._type = type
        self._thumb = None

        if type == theme.RESTORED:
            tmpfile = os.path.join(theme.SESSION_PATH, '.tmp.png')
            file(tmpfile, 'w').write(image)
            self._orig = theme.pixbuf(tmpfile)
            os.unlink(tmpfile)
            self._filename = 'ground.png'
        else:
            self._filename = image
            self._orig = theme.pixbuf(image)

    def custom(self):
        return self._type != theme.PREINSTALLED

    def read(self):
        pixbuf2str(self._orig)

    def filename(self):
        return self._filename

    def thumb(self):
        if not self._thumb:
            self._thumb = theme.scale(self._orig)
        return self._thumb

    def orig(self):
        return self._orig

    def select(self):
        if self._type != theme.CUSTOM:
            return self
        return theme.choose(
                lambda title, file: Ground(title, file, theme.JOURNAL))

THEMES = [
    Ground(_('Saturn'),     'images/backpics/bigbg01.gif', theme.PREINSTALLED),
    Ground(_('Snowflakes'), 'images/backpics/bigbg02.gif', theme.PREINSTALLED),
    Ground(_('Eye'),        'images/backpics/bigbg03.gif', theme.PREINSTALLED),
    Ground(_('Blobs'),      'images/backpics/bigbg04.gif', theme.PREINSTALLED),
    Ground(_('Star Night'), 'images/backpics/bigbg05.gif', theme.PREINSTALLED),
    Ground(_('Forest'),     'images/backpics/bigbg06.gif', theme.PREINSTALLED),
    Ground(_('Spiral'),     'images/backpics/bigbg07.gif', theme.PREINSTALLED),
    Ground(_('Beam'),       'images/backpics/bigbg08.gif', theme.PREINSTALLED),
    Ground(_('Cloth'),      'images/backpics/bigbg09.gif', theme.PREINSTALLED),
    Ground(_('Faces'),      'images/backpics/bigbg10.gif', theme.PREINSTALLED),
    Ground(_('Leaves'),     'images/backpics/bigbg11.gif', theme.PREINSTALLED),
    Ground(_('Vegetables'), 'images/backpics/bigbg12.gif', theme.PREINSTALLED),
    Ground(_('Spotlight'),  'images/backpics/bigbg13.gif', theme.PREINSTALLED),
    Ground(_('Strips'),     'images/backpics/bigbg14.gif', theme.PREINSTALLED),
    Ground(_('Scene'),      'images/backpics/bigbg15.gif', theme.PREINSTALLED),
    Ground(_('Rhombs'),     'images/backpics/bigbg16.gif', theme.PREINSTALLED),
    Ground(_('Milky Way'),  'images/backpics/bigbg17.gif', theme.PREINSTALLED),
    None,
    Ground(_('Custom'),     'images/backpics/custom.png', theme.CUSTOM)]
