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
#

### cartoonbuilder
###
### author: Ed Stoner (ed@whsd.net)
### (c) 2007 World Wide Workshop Foundation

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import cairo
import logging
logger = logging.getLogger('cartoon')
import theme

class Screen(Gtk.DrawingArea):
    def __init__(self):
        Gtk.DrawingArea.__init__(self)
        #self.cr = None  # initialized in realize-event handler
        self.width  = 0 # updated in size-allocate handler
        self.height = 0 # idem
        self.bgpixbuf = None
        self.fgpixbuf = None
        self.connect('size-allocate', self.on_size_allocate)
        self.connect('draw',  self.on_draw_cb)
        self.connect('realize',       self.on_realize)

    def on_realize(self, widget):
        #self.cr = widget.window.new_gc()
        pass

    def on_size_allocate(self, widget, allocation):
        self.height = self.width = min(allocation.width, allocation.height)
        logger.debug('pixmap')
        logger.debug(self.height)

    
    def on_draw_cb(self, widget, cr):
        # This is where the drawing takes place
        if self.bgpixbuf:
            pixbuf = self.bgpixbuf
            if pixbuf.get_width != self.width:
                pixbuf = theme.scale(pixbuf, self.width)
            logger.debug('cairo')
            logger.debug(pixbuf)
            logger.debug(cr)
            #widget.window.draw_pixbuf(self.gc, pixbuf, 0, 0, 0, 0, -1, -1, 0, 0)
            Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
            cr.rectangle(0, 0, -1, -1)
            cr.paint()


        if self.fgpixbuf:
            pixbuf = self.fgpixbuf
            if pixbuf.get_width != self.width:
                pixbuf = theme.scale(pixbuf, self.width)
            logger.debug('cairo1')
            logger.debug(pixbuf)
            logger.debug(cr)
            #widget.window.draw_pixbuf(self.gc, pixbuf, 0, 0, 0, 0, -1, -1, 0, 0)
            Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
            cr.rectangle(0, 0, -1, -1)
            cr.paint()

    def draw(self):
        self.queue_draw()
