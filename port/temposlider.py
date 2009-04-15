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

from sugar.graphics import style

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
        def map_range(value, ilower, iupper, olower, oupper):
            if value == iupper:
                return oupper
            return olower + int((oupper-olower+1) * (value-ilower) /
                    float(iupper-ilower))

        img = map_range(tempo, self.adjustment.lower,
                            self.adjustment.upper, 0, 7)

        if not self._pixbuf[img]:
            self._pixbuf[img] = gtk.gdk.pixbuf_new_from_file_at_size(
                    os.path.join(os.path.dirname(__file__), 'images',
                        'tempo' + str(img+1) + '.svg'),
                    style.STANDARD_ICON_SIZE, style.STANDARD_ICON_SIZE)

        self._image.set_from_pixbuf(self._pixbuf[img])

    def _press_cb(self, widget, event):
        self._active = True

    def _release_cb(self, widget, event):
        self._active = False
        if self._delayed != 0:
            self.set_value(self._delayed, True)
            self._delayed = 0
