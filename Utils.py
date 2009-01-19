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

from Theme import *
import sugar.graphics
from sugar.graphics import style

class FileInstanceVariable:
    def __init__(self, value = None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def __getitem__(self, key):
        return self.value[key]

class ComboBox(sugar.graphics.combobox.ComboBox):
    def __init__(self):
        sugar.graphics.combobox.ComboBox.__init__(self)
        self.set_name('we-really-need-it-to-use-custom-combobox-colors')

    def append_item(self, action_id, text = None, icon_name = None, size = None,
            pixbuf = None, position = None):

        if not self._icon_renderer and (icon_name or pixbuf):
            self._icon_renderer = gtk.CellRendererPixbuf()

            settings = self.get_settings()
            w, h = gtk.icon_size_lookup_for_settings(settings, gtk.ICON_SIZE_MENU)
            self._icon_renderer.props.stock_size = w

            self._icon_renderer.props.xpad = 4
            self._icon_renderer.props.ypad = 4

            self.pack_start(self._icon_renderer, False)
            self.add_attribute(self._icon_renderer, 'pixbuf', 2)

        if not self._text_renderer and text:
            self._text_renderer = gtk.CellRendererText()
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

def map_range(value, ilower, iupper, olower, oupper):
    if value == iupper:
        return oupper
    return olower + int((oupper-olower+1) * (value-ilower) /
            float(iupper-ilower))

class TempoSlider(gtk.HBox):
    def __init__(self, min_value, max_value):
        gtk.HBox.__init__(self)

        self._pixbuf = [None] * 8
        self._image = gtk.Image()
        self._image.show()

        # used to store tempo updates while the slider is active
        self._delayed = 0 
        self._active = False

        self.adjustment = gtk.Adjustment(min_value, min_value, max_value,
                (max_value - min_value) / 8, (max_value - min_value) / 8, 0)
        self._adjustment_h = self.adjustment.connect('value-changed',
                self._changed_cb)

        slider = gtk.HScale(adjustment = self.adjustment)
        slider.show()
        slider.set_draw_value(False)
        slider.connect("button-press-event", self._press_cb)
        slider.connect("button-release-event", self._release_cb)

        self.pack_start(slider, True, True)
        self.pack_end(self._image, False, False)

    def set_value(self, tempo, quiet = False):
        if self._active:
            self._delayed = tempo
        elif quiet:
            self.adjustment.handler_block(self._adjustment_h)
            self.adjustment.set_value(tempo)
            self._update(tempo)
            self.adjustment.handler_unblock(self._adjustment_h)
        else:
            self.adjustment.set_value(tempo)

    def _changed_cb(self, widget):
        self._update(widget.get_value())

    def _update(self, tempo):
        img = map_range(tempo, self.adjustment.lower,
                            self.adjustment.upper, 0, 7)

        if not self._pixbuf[img]:
            self._pixbuf[img] = gtk.gdk.pixbuf_new_from_file_at_size(
                    os.path.join(get_bundle_path(), 'icons/tempo' +
                        str(img+1) + '.svg'),
                    style.STANDARD_ICON_SIZE, style.STANDARD_ICON_SIZE)

        self._image.set_from_pixbuf(self._pixbuf[img])

    def _press_cb(self, widget, event):
        self._active = True

    def _release_cb(self, widget, event):
        self._active = False
        if self._delayed != 0:
            self.set_value(self._delayed, True)
            self._delayed = 0
