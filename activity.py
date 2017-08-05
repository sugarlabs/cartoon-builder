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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gettext import gettext as _

import logging
logger = logging.getLogger('cartoon-builder')

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton

from toolkit.temposlider import TempoSlider
from toolkit.activity import SharedActivity
from toolkit.toolbarbox import ToolbarBox
from toolkit.activity_widgets import *

import montage
import document
import char
import ground
import sound
from theme import *
from messenger import Messenger, SERVICE
from utils import *


class CartoonBuilderActivity(SharedActivity):
    def __init__(self, handle):
        self.notebook = Gtk.Notebook()
        SharedActivity.__init__(self, self.notebook, SERVICE, handle)

        self.notebook.show()
        self.notebook.props.show_border = False
        self.notebook.props.show_tabs = False

        self.montage = montage.View()
        self.notebook.append_page(self.montage, Gtk.Label(''))
     
        toolbox = ToolbarBox()
        toolbox.show()

        toolbox.toolbar.insert(ActivityToolbarButton(self), -1)

        separator = Gtk.SeparatorToolItem()
        separator.set_draw(False)
        toolbox.toolbar.insert(separator, -1)

        self.notebook_toolbar = Gtk.Notebook()
        self.notebook_toolbar.props.show_border = False
        self.notebook_toolbar.props.show_tabs = False
        self.notebook_toolbar.append_page(self._create_montage_toolbar(), Gtk.Label(''))
        self.notebook_toolbar.show()

        notebook_item = Gtk.ToolItem()
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
        toolbar = Gtk.Toolbar()

        playButtonImg = Gtk.Image()
        playButtonImg.show()
        playButtonImg.set_from_icon_name('media-playback-start',
                Gtk.IconSize.LARGE_TOOLBAR)

        pauseButtonImg = Gtk.Image()
        pauseButtonImg.show()
        pauseButtonImg.set_from_icon_name('media-playback-pause',
                Gtk.IconSize.LARGE_TOOLBAR)

        self.playButton = ToggleToolButton('media-playback-start')
        self.playButton.connect('toggled', self.__play_cb, playButtonImg,
                pauseButtonImg)
        toolbar.insert(self.playButton, -1)
        self.playButton.set_tooltip(_('Play / Pause'))

        tempo = TempoSlider(0, 10)
        tempo.adjustment.connect("value-changed", self.__tempo_cb)
        tempo.set_size_request(250, -1)
        tempo.set_value(5)
        tempo_item = Gtk.ToolItem()
        tempo_item.add(tempo)
        toolbar.insert(tempo_item, -1)

        separator = Gtk.SeparatorToolItem()
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
        self.montage.set_tempo(widget.get_value())

    def __play_cb(self, widget, playButtonImg, pauseButtonImg):
        if widget.get_active():
            widget.set_icon_widget(pauseButtonImg)
            sound.play()
            self.montage.play()
        else:
            widget.set_icon_widget(playButtonImg)
            sound.stop()
            self.montage.stop()
