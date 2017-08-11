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
from gi.repository import Gtk
from gi.repository import Gdk
from sugar3.graphics.icon import Icon

class ScrollButton(Gtk.ToolButton):
    def __init__(self, icon_name):
        Gtk.ToolButton.__init__(self)

        icon = Icon(icon_name = icon_name,
                icon_size=Gtk.IconSize.SMALL_TOOLBAR)
        # The alignment is a hack to work around Gtk.ToolButton code
        # that sets the icon_size when the icon_widget is a Gtk.Image
        alignment = Gtk.Alignment()
        alignment.set(0.5, 0.5, 0, 0)
        alignment.add(icon)
        self.set_icon_widget(alignment)

class ScrolledBox(Gtk.EventBox):
    def __init__(self, orientation,
            arrows_policy=Gtk.PolicyType.AUTOMATIC,
            scroll_policy=Gtk.PolicyType.AUTOMATIC):

        Gtk.EventBox.__init__(self)
        self.orientation = orientation
        self._viewport = None
        self._abox = None
        self._aviewport = None
        self._aviewport_sig = None
        self._arrows_policy = arrows_policy
        self._scroll_policy = scroll_policy
        self._left = None
        self._right = None

        if orientation == Gtk.Orientation.HORIZONTAL:
            box = Gtk.HBox()
        else:
            box = Gtk.VBox()
        if self._arrows_policy == Gtk.PolicyType.AUTOMATIC:
            box.connect("size-allocate", self._box_allocate_cb)
        self.add(box)

        if self._arrows_policy != Gtk.PolicyType.NEVER:
            if orientation == Gtk.Orientation.HORIZONTAL:
                self._left = ScrollButton('go-left')
            else:
                self._left = ScrollButton('go-up')
            self._left.connect('clicked', self._scroll_cb,
                    Gdk.ScrollDirection.LEFT)
            box.pack_start(self._left, False, False, 0)

        self._scrolled = Gtk.ScrolledWindow()
        if orientation == Gtk.Orientation.HORIZONTAL:
            self._scrolled.set_policy(scroll_policy, Gtk.PolicyType.NEVER)
        else:
            self._scrolled.set_policy(Gtk.PolicyType.NEVER, scroll_policy)
        self._scrolled.connect('scroll-event', self._scroll_event_cb)
        box.pack_start(self._scrolled, True, True, 0)

        if orientation == Gtk.Orientation.HORIZONTAL:
            self._adj = self._scrolled.get_hadjustment()
        else:
            self._adj = self._scrolled.get_vadjustment()
        self._adj.connect('changed', self._scroll_changed_cb)
        self._adj.connect('value-changed', self._scroll_changed_cb)

        if self._arrows_policy != Gtk.PolicyType.NEVER:
            if orientation == Gtk.Orientation.HORIZONTAL:
                self._right = ScrollButton('go-right')
            else:
                self._right = ScrollButton('go-down')
            self._right.connect('clicked', self._scroll_cb,
                    Gdk.ScrollDirection.RIGHT)
            box.pack_start(self._right, False, False, 0)

    def modify_fg(self, state, bg):
        Gtk.EventBox.modify_fg(self, state, bg)
        self._viewport.get_parent().modify_fg(state, bg)

    def modify_bg(self, state, bg):
        Gtk.EventBox.modify_bg(self, state, bg)
        self._viewport.get_parent().modify_bg(state, bg)

    def set_viewport(self, widget):
        if widget == self._viewport: return
        if self._viewport and self._aviewport_sig:
            self._viewport.disconnect(self._aviewport_sig)
        self._viewport = widget

        if self._arrows_policy == Gtk.PolicyType.AUTOMATIC:
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

        if self.orientation == Gtk.Orientation.HORIZONTAL:
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
        if self.orientation == Gtk.Orientation.HORIZONTAL:
            if event.direction == Gdk.ScrollDirection.UP:
                event.direction = Gdk.ScrollDirection.LEFT
            if event.direction == Gdk.ScrollDirection.DOWN:
                event.direction = Gdk.ScrollDirection.RIGHT
        else:
            if event.direction == Gdk.ScrollDirection.LEFT:
                event.direction = Gdk.ScrollDirection.UP
            if event.direction == Gdk.ScrollDirection.RIGHT:
                event.direction = Gdk.ScrollDirection.DOWN

        if self._scroll_policy == Gtk.PolicyType.NEVER:
            self._scroll_cb(None, event.direction)

        return False

    def _scroll_cb(self, widget, direction):
        if direction in (Gdk.ScrollDirection.LEFT, Gdk.ScrollDirection.UP):
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
    def __init__(self, **kwargs):
        ScrolledBox.__init__(self, Gtk.Orientation.HORIZONTAL, **kwargs)

class VScrolledBox(ScrolledBox):
    def __init__(self, **kwargs):
        ScrolledBox.__init__(self, Gtk.Orientation.VERTICAL, **kwargs)
