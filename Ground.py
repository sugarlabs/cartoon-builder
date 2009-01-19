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

THEMES = (
    { 'name'  : _('Saturn'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg01.gif'),
      'custom': None },
    { 'name'  : _('Snowflakes'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg02.gif'),
      'custom': None },
    { 'name'  : _('Yye'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg03.gif'),
      'custom': None },
    { 'name'  : _('Blobs'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg04.gif'),
      'custom': None },
    { 'name'  : _('Star Night'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg05.gif'),
      'custom': None },
    { 'name'  : _('Forest'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg06.gif'),
      'custom': None },
    { 'name'  : _('Spiral'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg07.gif'),
      'custom': None },
    { 'name'  : _('Spotlight'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg08.gif'),
      'custom': None },
    { 'name'  : _('Cloth'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg09.gif'),
      'custom': None },
    { 'name'  : _('Faces'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg10.gif'),
      'custom': None },
    { 'name'  : _('Leaves'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg11.gif'),
      'custom': None },
    { 'name'  : _('Vegetables'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg12.gif'),
      'custom': None },
    { 'name'  : _('Another Spotlight'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg13.gif'),
      'custom': None },
    { 'name'  : _('Strips'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg14.gif'),
      'custom': None },
    { 'name'  : _('Scene'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg15.gif'),
      'custom': None },
    { 'name'  : _('Rhombs'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg16.gif'),
      'custom': None },
    { 'name'  : _('Milky Way'),
      'pixbuf': Theme.pixmap('images/backpics/bigbg17.gif'),
      'custom': None },
    None,
    { 'name'  : _('Custom'),
      'pixbuf': Theme.pixmap('images/backpics/custom.png'),
      'custom': True } )

def change(theme):
    if theme['custom'] == None or theme['custom'] == False:
        return theme

    chooser = ObjectChooser(_('Choose background image'), None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
    try:
        result = chooser.run()

        if result == gtk.RESPONSE_ACCEPT:
            jobject = chooser.get_selected_object()
            if jobject and jobject.file_path:
                return { 'name'  : jobject.metadata['title'],
                         'pixbuf': Theme.pixmap(jobject.file_path),
                         'custom': False }
    finally:
        chooser.destroy()
        del chooser

    return None
