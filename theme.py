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
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import shutil
from math import ceil

from sugar3.activity.activity import get_bundle_path, get_activity_root
from sugar3.graphics import style

SOUND_SPEAKER = 'images/sounds/speaker.png'
SOUND_MUTE    = 'images/sounds/mute.png'
SOUND_CUSTOM  = 'images/sounds/custom.png'

LOGO_WIDTH = style.zoom(275)
TAPE_COUNT = 11
FRAME_COUNT = 14

DESKTOP_WIDTH = Gdk.Screen.width()
DESKTOP_HEIGHT = Gdk.Screen.height() - style.LARGE_ICON_SIZE

THUMB_SIZE = style.zoom(min(100, DESKTOP_WIDTH / (TAPE_COUNT+1)))

FRAME_COLS = style.zoom(max(1, ((DESKTOP_WIDTH-LOGO_WIDTH) -
        min(DESKTOP_HEIGHT-THUMB_SIZE-THUMB_SIZE/2, DESKTOP_WIDTH-LOGO_WIDTH))
        / THUMB_SIZE))

FRAME_ROWS = max((DESKTOP_HEIGHT - THUMB_SIZE*3) / THUMB_SIZE,
        int(ceil(float(FRAME_COUNT) / FRAME_COLS)))

BORDER_WIDTH = style.zoom(10)

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
    (Gtk.StateType.NORMAL,"#CCFF99"),
    (Gtk.StateType.ACTIVE,"#CCFF99"),
    (Gtk.StateType.PRELIGHT,"#CCFF99"),
    (Gtk.StateType.SELECTED,"#CCFF99"),
    (Gtk.StateType.INSENSITIVE,"#CCFF99"),
    ) # very light green
COLOR_BG_BUTTONS = (
    (Gtk.StateType.NORMAL,"#027F01"),
    (Gtk.StateType.ACTIVE,"#CCFF99"),
    (Gtk.StateType.PRELIGHT,"#016D01"),
    (Gtk.StateType.SELECTED,"#CCFF99"),
    (Gtk.StateType.INSENSITIVE,"#027F01"),
    )
OLD_COLOR_BG_BUTTONS = (
    (Gtk.StateType.NORMAL,"#027F01"),
    (Gtk.StateType.ACTIVE,"#014D01"),
    (Gtk.StateType.PRELIGHT,"#016D01"),
    (Gtk.StateType.SELECTED,"#027F01"),
    (Gtk.StateType.INSENSITIVE,"#027F01"),
    )

SESSION_PATH = os.path.join(get_activity_root(), 'tmp', '.session')
if os.path.isdir(SESSION_PATH):
    shutil.rmtree(SESSION_PATH)
os.mkdir(SESSION_PATH)

def path(*args):
    file = os.path.join(*args)

    if os.path.isabs(file):
        return file
    else:
        return os.path.join(get_bundle_path(), file)

def pixbuf(file, size = None):
    if size:
        out = GdkPixbuf.Pixbuf.new_from_file_at_size(path(file), size, size)
    else:
        out = GdkPixbuf.Pixbuf.new_from_file(path(file))
    return out

def scale(pixbuf, size = THUMB_SIZE):
    return pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)

EMPTY_FILENAME = 'images/pics/empty.png'
EMPTY_ORIG = pixbuf(EMPTY_FILENAME)
EMPTY_THUMB = scale(EMPTY_ORIG)

CUSTOM_FRAME_ORIG = pixbuf('images/pics/custom.png')
CUSTOM_FRAME_THUMB = scale(CUSTOM_FRAME_ORIG)

# customize theme
gtkrc = os.path.join(get_bundle_path(), 'gtkrc')
Gtk.rc_add_default_file(gtkrc)
settings = Gtk.Settings.get_default()
Gtk.rc_reset_styles(settings)
Gtk.rc_reparse_all_for_settings(settings, True)
