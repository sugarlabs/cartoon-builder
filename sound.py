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
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)
from gi.repository import Gtk
import shutil
from glob import glob
from gettext import gettext as _

import toolkit.chooser as chooser

import theme
from utils import *
from sugar3.activity.activity import get_bundle_path


def load():
    from document import Document

    if Document.sound and Document.sound.custom():
        THEMES.append(Document.sound)

class Sound:
    playing = False
    current = None
    player = None

    def __init__(self, name, id, soundfile, thumb):
        self.name = name
        self.id = id
        self._soundfile = soundfile
        self._thumb = theme.pixbuf(thumb, theme.THUMB_SIZE)

    def custom(self):
        return True

    def serialize(self):
        return file(self._soundfile, 'r').read()

    def thumb(self):
        return self._thumb

    def select(self):
        if Sound.current != self:
            Sound.current = self
            Sound.player.set_state(Gst.State.NULL)
            Sound.player.set_property('uri',
                    'file://' + theme.path(self._soundfile))
        if Sound.playing:
            Sound.player.set_state(Gst.State.PLAYING)
        return self

class PreinstalledSound(Sound):
    def __init__(self, name, filename):
        Sound.__init__(self, name, filename, filename, theme.SOUND_SPEAKER)

    def custom(self):
        return False

class MuteSound(Sound):
    def __init__(self, name):
        Sound.__init__(self, name, 'mute', None, theme.SOUND_MUTE)

    def custom(self):
        return False

    def serialize(self):
        return ''

    def select(self):
        Sound.current = self
        Sound.player.set_state(Gst.State.PAUSED)
        return self

class CustomSound(Sound):
    def __init__(self, name):
        Sound.__init__(self, name, None, None, theme.SOUND_CUSTOM)

    def select(self):
        sound = chooser.pick(lambda jobject: JournalSound(jobject),
                what=chooser.AUDIO)
        if sound:
            sound.select()
        return sound

class RestoredSound(Sound):
    def __init__(self, name, id, data):
        soundfile = os.path.join(theme.SESSION_PATH, id)
        Sound.__init__(self, name, id, soundfile, theme.SOUND_CUSTOM)
        file(soundfile, 'w').write(data)

class JournalSound(Sound):
    def __init__(self, jobject):
        soundfile = os.path.join(theme.SESSION_PATH, jobject.object_id)
        Sound.__init__(self, jobject.metadata['title'],
                jobject.object_id, soundfile, theme.SOUND_CUSTOM)
        shutil.copy(jobject.file_path, soundfile) 
        THEMES.append(self)

THEMES = [
    PreinstalledSound(_('Gobble'),  'sounds/gobble.wav'),
    PreinstalledSound(_('Funk'),    'sounds/funk.wav'),
    PreinstalledSound(_('Giggle'),  'sounds/giggle.wav'),
    PreinstalledSound(_('Jungle'),  'sounds/jungle.wav'),
    MuteSound(_('Mute')),
    None,
    CustomSound(_('Custom')) ]

def play():
    Sound.playing = True
    Sound.current.select()

def stop():
    Sound.playing = False
    Sound.player.set_state(Gst.State.PAUSED)

# GSTREAMER STUFF

def _reload_cb(bus, message):
    Sound.player.set_state(Gst.State.READY)
    Sound.player.set_state(Gst.State.PLAYING)

def _error_cb(bus, message):
    Sound.player.set_state(Gst.State.NULL)

Sound.player = Gst.ElementFactory.make("playbin", "player")
fakesink = Gst.ElementFactory.make('fakesink', "my-fakesink")
Sound.player.set_property("video-sink", fakesink)

bus = Sound.player.get_bus()
bus.add_signal_watch()
bus.connect('message::eos', _reload_cb)
bus.connect('message::error', _error_cb)
