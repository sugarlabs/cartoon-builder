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

import gtk
from gettext import gettext as _

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton

import montage
import lessons
import sound
from utils import *

class MontageToolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)

        self.playButton = ToggleToolButton('media-playback-start')
        self.playButton.connect('toggled', self._play_cb)
        self.insert(self.playButton, -1)
        self.playButton.set_tooltip(_('Play / Pause'))

        # Play button Image
        self.playButtonImg = gtk.Image()
        self.playButtonImg.show()
        self.playButtonImg.set_from_icon_name('media-playback-start', gtk.ICON_SIZE_LARGE_TOOLBAR)

        # Pause button Image
        self.pauseButtonImg = gtk.Image()
        self.pauseButtonImg.show()
        self.pauseButtonImg.set_from_icon_name('media-playback-pause', gtk.ICON_SIZE_LARGE_TOOLBAR)

        tempo = TempoSlider(0, 10)
        tempo.adjustment.connect("value-changed", self._tempo_cb)
        tempo.set_size_request(250, -1)
        tempo.set_value(5)
        tempo_item = gtk.ToolItem()
        tempo_item.add(tempo)
        self.insert(tempo_item, -1)

        separator = gtk.SeparatorToolItem()
        self.insert(separator,-1)

        clear_tape = ToolButton('sl-reset')
        clear_tape.connect('clicked', self._clear_tape_cb)
        clear_tape.set_tooltip(_(''))
        self.insert(clear_tape, -1)

        self.show_all()

    def _clear_tape_cb(self, widget):
        montage.clear_tape()

    def _tempo_cb(self, widget):
        montage.set_tempo(widget.value)

    def _play_cb(self, widget):
        if widget.get_active():
            widget.set_icon_widget(self.pauseButtonImg)
            sound.play()
            montage.play()
        else:
            widget.set_icon_widget(self.playButtonImg)
            sound.stop()
            montage.stop()

class LessonsToolbar(gtk.Toolbar):
    def __init__(self):
        gtk.Toolbar.__init__(self)
        self._mask = False

        for lesson in lessons.THEMES:
            button = gtk.ToggleToolButton()
            button.set_label(lesson.name)
            button.connect('clicked', self._lessons_cb, lesson)
            self.insert(button, -1)

        self.get_nth_item(0).set_active(True)
        self.show_all()

    def _lessons_cb(self, widget, lesson):
        if self._mask:
            return
        self._mask = True

        for i, j in enumerate(lessons.THEMES):
            if j != lesson:
                self.get_nth_item(i).set_active(False)

        widget.props.active = True
        lesson.change()
        self._mask = False
