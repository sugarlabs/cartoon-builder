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
from utils import *
from sugar.activity.activity import get_bundle_path

def load():
    from document import Document

    if Document.sound and Document.sound.custom():
        THEMES.insert(-1, Document.sound)

class Sound:
    playing = False
    current = None
    player = None

    def __init__(self, name, sound, type):
        self.name = name
        self._type = type

        def _tmpname():
            l = sorted(glob(os.path.join(theme.SESSION_PATH, 'sound*')))
            return os.path.join(theme.SESSION_PATH, 'sound.%03d' % (len(l)+1))

        if type == theme.RESTORED:
            self._thumb = theme.pixbuf(theme.SOUND_CUSTOM, theme.THUMB_SIZE)
            self._soundfile = _tmpname()
            file(self._soundfile, 'w').write(sound)
        elif type == theme.CUSTOM:
            self._thumb = theme.pixbuf(theme.SOUND_MUTE, theme.THUMB_SIZE)
            self._soundfile = ''
        elif type == theme.JOURNAL:
            self._thumb = theme.pixbuf(theme.SOUND_CUSTOM, theme.THUMB_SIZE)
            self._soundfile = _tmpname()
            os.rename(sound, self._soundfile) 
        else:
            self._thumb = theme.pixbuf(theme.SOUND_SPEAKER, theme.THUMB_SIZE)
            self._soundfile = sound

    def custom(self):
        return self._type != theme.PREINSTALLED

    def read(self):
        if not self._soundfile:
            return ''
        else:
            return file(self._soundfile, 'r').read()

    def filename(self):
        return self._soundfile

    def thumb(self):
        return self._thumb

    def select(self):
        out = self

        if self._type == theme.CUSTOM:
            out = theme.choose(
                    lambda title, file: Sound(title, file, theme.JOURNAL))
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
    Sound(_('Gobble'),  'sounds/gobble.wav', theme.PREINSTALLED),
    Sound(_('Funk'),    'sounds/funk.wav', theme.PREINSTALLED),
    Sound(_('Giggle'),  'sounds/giggle.wav', theme.PREINSTALLED),
    Sound(_('Jungle'),  'sounds/jungle.wav', theme.PREINSTALLED),
    Sound(_('Mute'),    '', theme.PREINSTALLED),
    None,
    Sound(_('Custom'),  None, theme.CUSTOM) ]

Sound.current = THEMES[0]

def play():
    Sound.playing = True
    Sound.current.select()

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
