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
import pango
import zipfile
import cStringIO

import sugar
from sugar.graphics import style
from sugar.graphics.icon import Icon

from theme import *

class Zip(zipfile.ZipFile):
    def __init__(self, *args):
        zipfile.ZipFile.__init__(self, *args)

    def write_pixbuf(self, arcfile, pixbuf):
        def push(data, buffer):
            buffer.write(data)

        buffer = cStringIO.StringIO()
        pixbuf.save_to_callback(push, 'png', user_data=buffer)
        self.writestr(arcfile, buffer.getvalue())

    def read_pixbuf(self, arcfile):
        tmpfile = os.path.join(SESSION_PATH, 'tmp.png')
        file(tmpfile, 'w').write(self.read(arcfile))
        out = gtk.gdk.pixbuf_new_from_file(tmpfile)
        os.unlink(tmpfile)
        return out

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

class ScrollButton(gtk.ToolButton):
    def __init__(self, icon_name):
        gtk.ToolButton.__init__(self)

        icon = Icon(icon_name = icon_name,
                icon_size=gtk.ICON_SIZE_SMALL_TOOLBAR)
        # The alignment is a hack to work around gtk.ToolButton code
        # that sets the icon_size when the icon_widget is a gtk.Image
        alignment = gtk.Alignment(0.5, 0.5)
        alignment.add(icon)
        self.set_icon_widget(alignment)
        
class ScrolledBox(gtk.EventBox):
    def __init__(self, orientation, arrows_policy = gtk.POLICY_AUTOMATIC):
        gtk.EventBox.__init__(self)
        self.orientation = orientation
        self._viewport = None
        self._abox = None
        self._aviewport = None
        self._aviewport_sig = None
        self._arrows_policy = arrows_policy
        self._left = None
        self._right = None

        if orientation == gtk.ORIENTATION_HORIZONTAL:
            box = gtk.HBox()
        else:
            box = gtk.VBox()
        if self._arrows_policy == gtk.POLICY_AUTOMATIC:
            box.connect("size-allocate", self._box_allocate_cb)
        self.add(box)

        if self._arrows_policy != gtk.POLICY_NEVER:
            if orientation == gtk.ORIENTATION_HORIZONTAL:
                self._left = ScrollButton('go-left')
            else:
                self._left = ScrollButton('go-up')
            self._left.connect('clicked', self._scroll_cb, 'left')
            box.pack_start(self._left, False, False, 0)

        self._scrolled = gtk.ScrolledWindow()
        if orientation == gtk.ORIENTATION_HORIZONTAL:
            self._scrolled.set_policy(arrows_policy, gtk.POLICY_NEVER)
        else:
            self._scrolled.set_policy(gtk.POLICY_NEVER, arrows_policy)
        self._scrolled.connect('scroll-event', self._scroll_event_cb)
        box.pack_start(self._scrolled, True, True, 0)

        if orientation == gtk.ORIENTATION_HORIZONTAL:
            self._adj = self._scrolled.get_hadjustment()
        else:
            self._adj = self._scrolled.get_vadjustment()
        self._adj.connect('changed', self._scroll_changed_cb)
        self._adj.connect('value-changed', self._scroll_changed_cb)

        if self._arrows_policy != gtk.POLICY_NEVER:
            if orientation == gtk.ORIENTATION_HORIZONTAL:
                self._right = ScrollButton('go-right')
            else:
                self._right = ScrollButton('go-down')
            self._right.connect('clicked', self._scroll_cb, 'right')
            box.pack_start(self._right, False, False, 0)

    def modify_fg(self, state, bg):
        gtk.EventBox.modify_fg(self, state, bg)
        self._viewport.get_parent().modify_fg(state, bg)

    def modify_bg(self, state, bg):
        gtk.EventBox.modify_bg(self, state, bg)
        self._viewport.get_parent().modify_bg(state, bg)

    def set_viewport(self, widget):
        if widget == self._viewport: return
        if self._viewport and self._aviewport_sig:
            self._viewport.disconnect(self._aviewport_sig)
        self._viewport = widget

        if self._arrows_policy == gtk.POLICY_AUTOMATIC:
            self._aviewport_sig = self._viewport.connect('size-allocate',
                    self._viewport_allocate_cb)

        self._scrolled.add_with_viewport(widget)

    def get_viewport_allocation(self):
        alloc = self._scrolled.get_allocation()
        alloc.x -= self._adj.get_value()
        return alloc

    def get_adjustment(self):
        return self._adj

    def _box_allocate_cb(self, w, a):
        self._abox = a
        self._update_arrows()

    def _viewport_allocate_cb(self, w, a):
        self._aviewport = a
        self._update_arrows()

    def _update_arrows(self):
        if not self._abox or not self._aviewport: return

        if self.orientation == gtk.ORIENTATION_HORIZONTAL:
            show_flag = self._abox.width < self._aviewport.width
        else:
            show_flag = self._abox.height < self._aviewport.height

        if show_flag:
            self._left.show()
            self._right.show()
        else:
            self._left.hide()
            self._right.hide()

    def _scroll_event_cb(self, widget, event):
        if self.orientation == gtk.ORIENTATION_HORIZONTAL:
            if event.direction == gtk.gdk.SCROLL_UP:
                event.direction = gtk.gdk.SCROLL_LEFT
            if event.direction == gtk.gdk.SCROLL_DOWN:
                event.direction = gtk.gdk.SCROLL_RIGHT
        else:
            if event.direction == gtk.gdk.SCROLL_LEFT:
                event.direction = gtk.gdk.SCROLL_UP
            if event.direction == gtk.gdk.SCROLL_RIGHT:
                event.direction = gtk.gdk.SCROLL_DOWN
        return False

    def _scroll_cb(self, widget, data):
        if data == 'left':
            val = max(self._adj.get_property('lower'), self._adj.get_value()
                    - self._adj.get_property('page_increment'))
        else:
            val = min(self._adj.get_property('upper')
                    - self._adj.get_property('page_size'),
                    self._adj.get_value()
                    + self._adj.get_property('page_increment'))

        self._adj.set_value(val)

    def _scroll_changed_cb(self, widget):
        val = self._adj.get_value()
        if self._left:
            if val == 0:
                self._left.set_sensitive(False)
            else:
                self._left.set_sensitive(True)

        if self._right:
            if val >= self._adj.get_property('upper') - \
                    self._adj.get_property('page_size'):
                self._right.set_sensitive(False)
            else:
                self._right.set_sensitive(True)

class HScrolledBox(ScrolledBox):
    def __init__(self, *args):
        ScrolledBox.__init__(self, gtk.ORIENTATION_HORIZONTAL, *args)

class VScrolledBox(ScrolledBox):
    def __init__(self, *args):
        ScrolledBox.__init__(self, gtk.ORIENTATION_VERTICAL, *args)
