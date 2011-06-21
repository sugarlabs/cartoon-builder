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

from toolkit.temposlider import TempoSlider
from toolkit.activity import SharedActivity
from toolkit.toolbarbox import ToolbarBox
from toolkit.activity_widgets import *

import montage
import lessons
import document
import char
import ground
import sound
import theme
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

        toolbox = ToolbarBox()
        toolbox.show()

        toolbox.toolbar.insert(ActivityToolbarButton(self), -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        toolbox.toolbar.insert(separator, -1)

        lessons_button = ToggleToolButton('mamamedia')
        lessons_button.connect('toggled', self.__toggled_lessons_button_cb)
        lessons_button.set_tooltip(_('Lessons'))
        toolbox.toolbar.insert(lessons_button, -1)

        separator = gtk.SeparatorToolItem()
        separator.set_draw(False)
        toolbox.toolbar.insert(separator, -1)

        self.notebook_toolbar = gtk.Notebook()
        self.notebook_toolbar.props.show_border = False
        self.notebook_toolbar.props.show_tabs = False
        self.notebook_toolbar.append_page(self._create_montage_toolbar())
        self.notebook_toolbar.append_page(self._create_lessons_toolbar())
        self.notebook_toolbar.show()

        notebook_item = gtk.ToolItem()
        notebook_item.set_expand(True)
        notebook_item.add(self.notebook_toolbar)
        notebook_item.show()
        toolbox.toolbar.insert(notebook_item, -1)

        toolbox.toolbar.insert(StopButton(self), -1)

        toolbox.show_all()
        self.toolbar_box = toolbox

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

    def _create_montage_toolbar(self):
        toolbar = gtk.Toolbar()

        playButtonImg = gtk.Image()
        playButtonImg.show()
        playButtonImg.set_from_icon_name('media-playback-start',
                gtk.ICON_SIZE_LARGE_TOOLBAR)

        pauseButtonImg = gtk.Image()
        pauseButtonImg.show()
        pauseButtonImg.set_from_icon_name('media-playback-pause',
                gtk.ICON_SIZE_LARGE_TOOLBAR)

        self.playButton = ToggleToolButton('media-playback-start')
        self.playButton.connect('toggled', self.__play_cb, playButtonImg,
                pauseButtonImg)
        toolbar.insert(self.playButton, -1)
        self.playButton.set_tooltip(_('Play / Pause'))

        tempo = TempoSlider(0, 10)
        tempo.adjustment.connect("value-changed", self.__tempo_cb)
        tempo.set_size_request(250, -1)
        tempo.set_value(5)
        tempo_item = gtk.ToolItem()
        tempo_item.add(tempo)
        toolbar.insert(tempo_item, -1)

        separator = gtk.SeparatorToolItem()
        toolbar.insert(separator,-1)

        clear_tape = ToolButton('sl-reset')
        clear_tape.connect('clicked', self.__clear_tape_cb)
        clear_tape.set_tooltip(_('Reset'))
        toolbar.insert(clear_tape, -1)

        toolbar.show_all()

        return toolbar

    def __clear_tape_cb(self, widget):
        for i in range(theme.TAPE_COUNT):
            self.montage.props.frame = (i, None)

    def __tempo_cb(self, widget):
        self.montage.set_tempo(widget.value)

    def __play_cb(self, widget, playButtonImg, pauseButtonImg):
        if widget.get_active():
            widget.set_icon_widget(pauseButtonImg)
            sound.play()
            self.montage.play()
        else:
            widget.set_icon_widget(playButtonImg)
            sound.stop()
            self.montage.stop()

    def _create_lessons_toolbar(self):
        toolbar = gtk.Toolbar()

        for lesson in lessons.THEMES:
            button = gtk.RadioToolButton()
            button.set_label(lesson.name)
            if toolbar.get_n_items():
                button.props.group = toolbar.get_nth_item(0)
            button.connect('clicked', self.__lesson_clicked_cb, lesson)
            toolbar.insert(button, -1)

        toolbar.get_nth_item(0).set_active(True)
        toolbar.show_all()

        return toolbar

    def __lesson_clicked_cb(self, widget, lesson):
        lesson.change()

    def __toggled_lessons_button_cb(self, button):
        page = button.props.active and 1 or 0
        self.notebook_toolbar.set_current_page(page)
        self.notebook.set_current_page(page)
        self.playButton.props.active = False
