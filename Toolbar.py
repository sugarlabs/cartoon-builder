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
from gettext import gettext as _

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.activity.activity import get_bundle_path

import Sound
from Utils import *

class Toolbar(gtk.Toolbar):
    def __init__(self, activity, app):
        gtk.Toolbar.__init__(self)
        self.activity = activity
        self.app = app

        self.playButton = ToggleToolButton('media-playback-start')
        self.playButton.connect('toggled', self._play_cb)
        self.insert(self.playButton, -1)
        self.playButton.show()
        self.playButton.set_tooltip(_('Play / Pause'))

        # Play button Image
        self.playButtonImg = gtk.Image()
        self.playButtonImg.set_from_icon_name('media-playback-start', gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.playButtonImg.show()

        # Pause button Image
        self.pauseButtonImg = gtk.Image()
        self.pauseButtonImg.set_from_icon_name('media-playback-pause', gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.pauseButtonImg.show()

        tempo = TempoSlider(0, 10)
        tempo.adjustment.connect("value-changed", self._tempo_cb)
        tempo.set_size_request(250, -1)
        tempo.set_value(5)
        tempo_item = gtk.ToolItem()
        tempo_item.add(tempo)
        self.insert(tempo_item, -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        self.insert(separator,-1)

        clear_tape = ToolButton('sl-reset')
        clear_tape.connect('clicked', self._clear_tape_cb)
        clear_tape.set_tooltip(_(''))
        self.insert(clear_tape, -1)

        self.show_all()

    def _clear_tape_cb(self, widget):
        self.app.set_tempo(widget.value)

    def _tempo_cb(self, widget):
        self.app.set_tempo(widget.value)

    def _play_cb(self, widget):
        if widget.get_active():
            widget.set_icon_widget(self.pauseButtonImg)
            Sound.play()
            self.app.play()
        else:
            widget.set_icon_widget(self.playButtonImg)
            Sound.stop()
            self.app.stop()
