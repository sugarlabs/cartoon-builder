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
import pango

from sugar.graphics import style
from sugar.graphics.icon import Icon
from sugar.graphics.icon import Icon
from sugar.graphics.combobox import ComboBox as _ComboBox

from theme import *

class ComboBox(_ComboBox):
    def __init__(self):
        _ComboBox.__init__(self)
        self.set_name('we-really-need-it-to-use-custom-combobox-colors')

    def append_item(self, action_id, text = None, icon_name = None, size = None,
            pixbuf = None, position = None):

        if not self._icon_renderer and (icon_name or pixbuf):
            self._icon_renderer = gtk.CellRendererPixbuf()

            settings = self.get_settings()
            w, h = gtk.icon_size_lookup_for_settings(settings,
                    gtk.ICON_SIZE_MENU)
            self._icon_renderer.props.stock_size = w

            self._icon_renderer.props.xpad = 4
            self._icon_renderer.props.ypad = 4

            self.pack_start(self._icon_renderer, False)
            self.add_attribute(self._icon_renderer, 'pixbuf', 2)

        if not self._text_renderer and text:
            self._text_renderer = gtk.CellRendererText()
            self._text_renderer.props.ellipsize = pango.ELLIPSIZE_END
            self.pack_end(self._text_renderer, True)
            self.add_attribute(self._text_renderer, 'text', 1)

        if not pixbuf:
            if icon_name:
                if not size:
                    size = gtk.ICON_SIZE_LARGE_TOOLBAR
                    width, height = gtk.icon_size_lookup(size)
                else:
                    width, height = size
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon_name,
                        width, height)
            else:
                pixbuf = None

        if position:
            self._model.insert(position, [action_id, text, pixbuf, False])
        else:
            self._model.append([action_id, text, pixbuf, False])
