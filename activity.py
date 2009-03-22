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

import logging
logger = logging.getLogger('cartoon-builder')

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.activity.activity import ActivityToolbox

import montage
import lessons
import document
import char
import ground
import sound
import theme
from shared import SharedActivity
from messenger import Messenger, SERVICE
from utils import *

class CartoonBuilderActivity(SharedActivity):
    def __init__(self, handle):
        self.notebook = gtk.Notebook()
        SharedActivity.__init__(self, self.notebook, SERVICE, handle)

        self.notebook.show()
        self.notebook.props.show_border = False
        self.notebook.props.show_tabs = False

        self.montage = montage.View()
        self.notebook.append_page(self.montage)
        self.lessons = lessons.View()
        self.lessons.show()
        self.notebook.append_page(self.lessons)

        toolbox = ActivityToolbox(self)
        toolbox.show()
        toolbox.connect('current-toolbar-changed', self._toolbar_changed_cb)
        self.set_toolbox(toolbox)

        montage_bar = MontageToolbar(self.montage)
        montage_bar.show()
        toolbox.add_toolbar(_('Montage'), montage_bar)

        lessons_bar = LessonsToolbar()
        lessons_bar.show()
        toolbox.add_toolbar(_('Lessons'), lessons_bar)

        toolbox.set_current_toolbar(1)

    def new_instance(self):
        logger.debug('new_instance')
        self.montage.restore()

    def resume_instance(self, filepath):
        logger.debug('resume_instance from %s' % filepath)
        document.load(filepath)
        char.load()
        ground.load()
        sound.load()
        self.montage.restore()

    def save_instance(self, filepath):
        logger.debug('save_instance to %s' % filepath)
        document.save(filepath)

    def share_instance(self, tube_conn, initiating):
        logger.debug('share_instance')
        self.messenger = Messenger(tube_conn, initiating, self.montage)

    def _toolbar_changed_cb(self, widget, index):
        if index == 2:
            self.notebook.set_current_page(1)
        else:
            self.notebook.set_current_page(0)

class MontageToolbar(gtk.Toolbar):
    def __init__(self, montage):
        gtk.Toolbar.__init__(self)
        self.montage = montage

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
        clear_tape.set_tooltip(_('Reset'))
        self.insert(clear_tape, -1)

        self.show_all()

    def _clear_tape_cb(self, widget):
        for i in range(theme.TAPE_COUNT):
            self.montage.props.frame = (i, None)

    def _tempo_cb(self, widget):
        self.montage.set_tempo(widget.value)

    def _play_cb(self, widget):
        if widget.get_active():
            widget.set_icon_widget(self.pauseButtonImg)
            sound.play()
            self.montage.play()
        else:
            widget.set_icon_widget(self.playButtonImg)
            sound.stop()
            self.montage.stop()

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
