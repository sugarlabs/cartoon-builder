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

"""gtk.gdk.Pixbuf extensions"""

import re
import os
import cStringIO
import gtk
import rsvg
import cairo
import logging

from sugar.graphics.xocolor import XoColor
from sugar.util import LRU

def to_file(pixbuf):
    """Convert pixbuf object to file object"""

    def push(pixbuf, buffer):
        buffer.write(pixbuf)

    buffer = cStringIO.StringIO()
    pixbuf.save_to_callback(push, 'png', user_data=buffer)
    buffer.seek(0)

    return buffer

def to_str(pixbuf):
    """Convert pixbuf object to string"""
    return to_file(pixbuf).getvalue()

def from_str(str):
    """Convert string to pixbuf object"""

    loader = gtk.gdk.pixbuf_loader_new_with_mime_type('image/png')
    loader.write(str)
    loader.close()

    return loader.get_pixbuf()

def from_svg_at_size(filename=None, width=None, height=None, handle=None,
        keep_ratio=True):
    """Scale and load SVG into pixbuf"""

    if not handle:
        handle = rsvg.Handle(filename)

    dimensions = handle.get_dimension_data()
    icon_width = dimensions[0]
    icon_height = dimensions[1]

    if icon_width != width or icon_height != height:
        ratio_width = float(width) / icon_width
        ratio_height = float(height) / icon_height

        if keep_ratio:
            ratio = min(ratio_width, ratio_height)
            if ratio_width != ratio:
                ratio_width = ratio
                width = int(icon_width * ratio)
            elif ratio_height != ratio:
                ratio_height = ratio
                height = int(icon_height * ratio)
    else:
        ratio_width = 1
        ratio_height = 1

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    context.scale(ratio_width, ratio_height)
    handle.render_cairo(context)

    loader = gtk.gdk.pixbuf_loader_new_with_mime_type('image/png')
    surface.write_to_png(loader)
    loader.close()

    return loader.get_pixbuf()

def sugar_icon(file_name=None, icon_name=None,
               width=None, height=None,
               color=None,
               insensitive_widget=None):
    """Load sugar icon into pixbuf

    NOTE: Function can load all image formats but makes sense only for SVG
          (due to color argument, see load_svg())

    NOTE: Function caches results

    Arguments:
        file_name           path to filename with image
                            (mutually exclusive for icon_name)
        icon_name           name of icon
                            (mutually exclusive for icon_name)
        width               width of final image
        height              height of final image
        color               defines stroke and fill colors for final SVG image
                            in string notion, could be:
                            * tuple of (stroke_color, fill_color)
                            * XoColor
                            * scalar value for stroke and fill colors
        insensitive_widget  render icon in insensitive mode
    """
    def load_svg():
        entities = {}
        if fill_color:
            entities['fill_color'] = fill_color
        if stroke_color:
            entities['stroke_color'] = stroke_color

        f = open(icon_filename, 'r')
        icon = f.read()
        f.close()

        for entity, value in entities.items():
            xml = '<!ENTITY %s "%s">' % (entity, value)
            icon = re.sub('<!ENTITY %s .*>' % entity, xml, icon)

        return rsvg.Handle(data=icon)

    def get_insensitive_pixbuf():
        if not (insensitive_widget and insensitive_widget.style):
            return pixbuf

        icon_source = gtk.IconSource()
        # Special size meaning "don't touch"
        icon_source.set_size(-1)
        icon_source.set_pixbuf(pixbuf)
        icon_source.set_state(gtk.STATE_INSENSITIVE)
        icon_source.set_direction_wildcarded(False)
        icon_source.set_size_wildcarded(False)

        # Please note that the pixbuf returned by this function is leaked
        # with current stable versions of pygtk. The relevant bug is
        # http://bugzilla.gnome.org/show_bug.cgi?id=502871
        #   -- 2007-12-14 Benjamin Berg
        pixbuf = insensitive_widget.style.render_icon(icon_source,
                insensitive_widget.get_direction(), gtk.STATE_INSENSITIVE, -1,
                insensitive_widget, "sugar-icon")

        return pixbuf

    def get_cache_key():
        return (icon_filename, fill_color, stroke_color, width, height,
                insensitive_widget is None)

    if isinstance(color, XoColor):
        stroke_color = color.get_stroke_color()
        fill_color = color.get_fill_color()
    elif isinstance(color, tuple):
        stroke_color = color[0]
        fill_color = color[1]
    else:
        stroke_color = color
        fill_color = color

    if file_name:
        icon_filename = file_name
    elif icon_name:
        theme = gtk.icon_theme_get_default()
        info = theme.lookup_icon(icon_name, width or 50, 0)
        if info:
            icon_filename = info.get_filename()
            del info
        else:
            logging.warning('No icon with the name %s '
                            'was found in the theme.' % icon_name)
    else:
        return None

    cache_key = get_cache_key()
    if cache_key in _sugar_icon_cache:
        return _sugar_icon_cache[cache_key]

    logging.debug('sugar_icon: file_name=%s icon_name=%s width=%s height=%s ' \
                  'color=%s' % (file_name, icon_name, width, height, color))

    is_svg = icon_filename.endswith('.svg')

    if is_svg:
        handle = load_svg()
        if width and height:
            pixbuf = from_svg_at_size(handle=handle, width=width, height=height,
                    keep_ratio=True)
        else:
            pixbuf = handle.get_pixbuf()
    else:
        if width and height:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon_filename,
                    width, height)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(icon_filename)

    if insensitive_widget:
        pixbuf = get_insensitive_pixbuf()

    _sugar_icon_cache[cache_key] = pixbuf

    return pixbuf

_sugar_icon_cache = LRU(50)
