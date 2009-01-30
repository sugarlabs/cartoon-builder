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

import Theme
from Utils import *
from sugar.activity.activity import get_bundle_path

TYPE_PREISTALLED = 0
TYPE_CUSTOM      = 1
TYPE_JOURNAL     = 2

def load():
    sound = Document.sound()
    custom = Sound(sound[0], 'images/sounds/speaker.png', sound[1])
    THEMES.insert(-1, custom)

class Sound:
    playing = False
    current = None
    player = None

    def __init__(self, name, file, sound, type):
        self.name = name
        self._thumb = Theme.pixbuf(file, THUMB_SIZE)
        self._type = type

        if type == TYPE_JOURNAL:
            l = sorted(glob(os.path.join(Theme.SESSION_PATH, 'sound*')))
            self._sound = os.path.join(Theme.SESSION_PATH,
                    'sound.%03d' % (len(l)+1))
            os.rename(sound, self._sound) 
        else:
            self._sound = sound

    def thumb(self):
        return self._thumb

    def change(self):
        out = self

        if self._type == TYPE_CUSTOM:
            out = Theme.choose(
                    lambda title, file: Sound(title,
                    'images/sounds/speaker.png', file, TYPE_JOURNAL))
            if not out:
                return None

        Sound.current = self
        if not Sound.playing: return out
        Sound.player.set_state(gst.STATE_NULL)
        if not out._sound: return out

        Sound.player.set_property('uri', 'file://' + Theme.path(out._sound))
        Sound.player.set_state(gst.STATE_NULL)
        Sound.player.set_state(gst.STATE_PLAYING)

        return out

THEMES = (
    Sound(_('Gobble'),  'images/sounds/speaker.png', 'sounds/gobble.wav',
                        TYPE_PREISTALLED),
    Sound(_('Funk'),    'images/sounds/speaker.png', 'sounds/funk.wav',
                        TYPE_PREISTALLED),
    Sound(_('Giggle'),  'images/sounds/speaker.png', 'sounds/giggle.wav',
                        TYPE_PREISTALLED),
    Sound(_('Jungle'),  'images/sounds/speaker.png', 'sounds/jungle.wav',
                        TYPE_PREISTALLED),
    Sound(_('Mute'),    'images/sounds/mute.png', None,
                        TYPE_PREISTALLED),
    None,
    Sound(_('Custom'),  'images/sounds/custom.png', None,
                        TYPE_CUSTOM) )
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
