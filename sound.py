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
import gst
from glob import glob
from gettext import gettext as _

import theme
from document import Document
from utils import *
from sugar.activity.activity import get_bundle_path

PREISTALLED = 0
CUSTOM      = 1
TEMPORARY   = 2
JOURNAL     = 3

def load():
    if os.path.isabs(Document.sound_filename):
        custom = Sound(Document.sound_name, 'images/sounds/speaker.png',
                Document.sound_filename, TEMPORARY)
        THEMES.insert(-1, custom)

class Sound:
    playing = False
    current = None
    player = None

    def __init__(self, name, imgfile, soundfile, type):
        self.name = name
        self._thumb = theme.pixbuf(imgfile, THUMB_SIZE)
        self._type = type

        if type == JOURNAL:
            l = sorted(glob(os.path.join(theme.SESSION_PATH, 'sound*')))
            self._soundfile = os.path.join(theme.SESSION_PATH,
                    'sound.%03d' % (len(l)+1))
            os.rename(soundfile, self._soundfile) 
        else:
            self._soundfile = soundfile

    def filename(self):
        return self._soundfile

    def thumb(self):
        return self._thumb

    def change(self):
        out = self

        if self._type == CUSTOM:
            out = theme.choose(
                    lambda title, file: Sound(title,
                    'images/sounds/speaker.png', file, JOURNAL))
            if not out:
                return None

        Sound.current = self
        if not Sound.playing: return out
        Sound.player.set_state(gst.STATE_NULL)
        if len(out._soundfile) == 0: return out

        Sound.player.set_property('uri', 'file://' + theme.path(out._soundfile))
        Sound.player.set_state(gst.STATE_NULL)
        Sound.player.set_state(gst.STATE_PLAYING)

        return out

THEMES = [
    Sound(_('Gobble'),  'images/sounds/speaker.png', 'sounds/gobble.wav',
                        PREISTALLED),
    Sound(_('Funk'),    'images/sounds/speaker.png', 'sounds/funk.wav',
                        PREISTALLED),
    Sound(_('Giggle'),  'images/sounds/speaker.png', 'sounds/giggle.wav',
                        PREISTALLED),
    Sound(_('Jungle'),  'images/sounds/speaker.png', 'sounds/jungle.wav',
                        PREISTALLED),
    Sound(_('Mute'),    'images/sounds/mute.png', '',
                        PREISTALLED),
    None,
    Sound(_('Custom'),  'images/sounds/custom.png', None,
                        CUSTOM)]

Sound.current = THEMES[0]

def play():
    Sound.playing = True
    Sound.current.change()

def stop():
    Sound.playing = False
    Sound.player.set_state(gst.STATE_NULL)

# GSTREAMER STUFF

def _gstmessage_cb(bus, message):
    type = message.type

    if type == gst.MESSAGE_EOS:
        # END OF SOUND FILE
        Sound.player.set_state(gst.STATE_NULL)
        Sound.player.set_state(gst.STATE_PLAYING)
    elif type == gst.MESSAGE_ERROR:
        Sound.player.set_state(gst.STATE_NULL)

Sound.player = gst.element_factory_make("playbin", "player")
fakesink = gst.element_factory_make('fakesink', "my-fakesink")
Sound.player.set_property("video-sink", fakesink)

bus = Sound.player.get_bus()
bus.add_signal_watch()
bus.connect('message', _gstmessage_cb)
