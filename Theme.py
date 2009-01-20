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

from sugar.activity.activity import get_bundle_path
from sugar.graphics import style

TRANSIMG = '50x50blank-trans.png'

DESKTOP_WIDTH = gtk.gdk.screen_width()
DESKTOP_HEIGHT = gtk.gdk.screen_height() - style.LARGE_ICON_SIZE

THUMB_SIZE = min(100, min(DESKTOP_WIDTH, DESKTOP_HEIGHT) / 8)
SCREEN_SIZE = min(DESKTOP_WIDTH - 275, DESKTOP_HEIGHT) - THUMB_SIZE*2 

FRAME_COUNT = DESKTOP_HEIGHT / THUMB_SIZE*2
TAPE_COUNT = (DESKTOP_WIDTH - THUMB_SIZE) / THUMB_SIZE

BORDER_LEFT = 1
BORDER_RIGHT = 2
BORDER_TOP = 4
BORDER_BOTTOM = 8
BORDER_VERTICAL = BORDER_TOP | BORDER_BOTTOM
BORDER_HORIZONTAL = BORDER_LEFT | BORDER_RIGHT
BORDER_ALL = BORDER_VERTICAL | BORDER_HORIZONTAL
BORDER_ALL_BUT_BOTTOM = BORDER_HORIZONTAL | BORDER_TOP
BORDER_ALL_BUT_LEFT = BORDER_VERTICAL | BORDER_RIGHT

SLICE_BTN_WIDTH = 40

# Colors from the Rich's UI design

GRAY = "#B7B7B7" # gray
PINK = "#FF0099" # pink
YELLOW = "#FFFF00" # yellow
WHITE = "#FFFFFF"
BLACK = "#000000"
BACKGROUND = "#66CC00" # light green
BUTTON_FOREGROUND = "#CCFB99" # very light green
BUTTON_BACKGROUND = "#027F01" # dark green
COLOR_FG_BUTTONS = (
    (gtk.STATE_NORMAL,"#CCFF99"),
    (gtk.STATE_ACTIVE,"#CCFF99"),
    (gtk.STATE_PRELIGHT,"#CCFF99"),
    (gtk.STATE_SELECTED,"#CCFF99"),
    (gtk.STATE_INSENSITIVE,"#CCFF99"),
    ) # very light green
COLOR_BG_BUTTONS = (
    (gtk.STATE_NORMAL,"#027F01"),
    (gtk.STATE_ACTIVE,"#CCFF99"),
    (gtk.STATE_PRELIGHT,"#016D01"),
    (gtk.STATE_SELECTED,"#CCFF99"),
    (gtk.STATE_INSENSITIVE,"#027F01"),
    )
OLD_COLOR_BG_BUTTONS = (
    (gtk.STATE_NORMAL,"#027F01"),
    (gtk.STATE_ACTIVE,"#014D01"),
    (gtk.STATE_PRELIGHT,"#016D01"),
    (gtk.STATE_SELECTED,"#027F01"),
    (gtk.STATE_INSENSITIVE,"#027F01"),
    )

def path(file):
    if os.path.isabs(file):
        return file
    else:
        return os.path.join(get_bundle_path(), file)

def pixbuf(file, size = None):
    if size:
        out = gtk.gdk.pixbuf_new_from_file_at_size(path(file), size, size)
    else:
        out = gtk.gdk.pixbuf_new_from_file(path(file))
    return out

# customize theme
gtkrc = os.path.join(get_bundle_path(), 'gtkrc')
gtk.rc_add_default_file(gtkrc)
settings = gtk.settings_get_default()
gtk.rc_reset_styles(settings)
gtk.rc_reparse_all_for_settings(settings, True)
