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
from gettext import gettext as _

import Theme
from Utils import *
from sugar.activity.activity import get_bundle_path

sound_icon = Theme.pixmap('icons/sound_icon.png')

THEMES = (
    { 'name'  : _('Custom'),
      'pixbuf': sound_icon,
      'sound' : None },

    { 'name'  :  _('Gobble'),
      'pixbuf': sound_icon,
      'sound' : 'sounds/gobble.wav' },

    { 'name'  : _('Funk'),
      'pixbuf': sound_icon,
      'sound' : 'sounds/funk.wav' },

    { 'name'  : _('Giggle'),
      'pixbuf': sound_icon,
      'sound' : 'sounds/giggle.wav' },

    { 'name'  : _('Jungle'),
      'pixbuf': sound_icon,
      'sound' : 'sounds/jungle.wav' },

    { 'name'  : _('Mute'),
      'pixbuf': sound_icon,
      'sound' : None } )

theme = FileInstanceVariable(THEMES[0])
playing = FileInstanceVariable(False)

def play():
    playing.set(True)
    change(theme.get())

def stop():
    playing.set(False)
    player.set_state(gst.STATE_NULL)

def change(a_theme):
    if not a_theme: return
    theme.set(a_theme)

    if not playing.get(): return

    player.set_state(gst.STATE_NULL)

    sound = theme['sound']
    if not sound: return

    player.set_property('uri', 'file://' + Theme.path(sound))
    player.set_state(gst.STATE_NULL)
    player.set_state(gst.STATE_PLAYING)

# GSTREAMER STUFF

def _gstmessage_cb(bus, message):
    t = message.type
    if t == gst.MESSAGE_EOS:
        # END OF SOUND FILE
        player.set_state(gst.STATE_NULL)
        player.set_state(gst.STATE_PLAYING)
    elif t == gst.MESSAGE_ERROR:
        player.set_state(gst.STATE_NULL)

player = gst.element_factory_make("playbin", "player")
fakesink = gst.element_factory_make('fakesink', "my-fakesink")
player.set_property("video-sink", fakesink)

bus = player.get_bus()
bus.add_signal_watch()
bus.connect('message', _gstmessage_cb)
