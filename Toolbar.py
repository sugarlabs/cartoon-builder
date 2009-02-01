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
    def __init__(self, activity, view):
        gtk.Toolbar.__init__(self)
        self.activity = activity
        self.view = view

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
        self.view.clear_tape()

    def _tempo_cb(self, widget):
        self.view.set_tempo(widget.value)

    def _play_cb(self, widget):
        if widget.get_active():
            widget.set_icon_widget(self.pauseButtonImg)
            Sound.play()
            self.view.play()
        else:
            widget.set_icon_widget(self.playButtonImg)
            Sound.stop()
            self.view.stop()

"""
SPANISH = u'Espa\xf1ol'
#SPANISH = 'Espanol'
LANGLIST = ['English',SPANISH]
LANG = {'English':{'character':'My Character',
                   'sound':'My Sound',
                   'background':'My Background',
                   'lessonplan':'Lesson Plans',
                   'lpdir':'lp-en'},
        SPANISH:{'character':u'Mi car\xe1cter',
                 'sound':'Mi sonido',
                 'background':'Mi fondo',
                 'lessonplan':u'Planes de la lecci\xf3n',
                 'lpdir':'lp-es'}}


def getwrappedfile(filepath,linelength):
    text = []
    f = file(filepath)
    for line in f:
        if line == '\n':
            text.append(line)
        else:
            for wline in textwrap.wrap(line.strip()):
                text.append('%s\n' % wline)
    return ''.join(text)




    def showlessonplans(self, widget, data=None):
        dia = gtk.Dialog(title='Lesson Plans',
                         parent=None,
                         flags=0,
                         buttons=None)
        dia.set_default_size(500,500)
        dia.show()

        #dia.vbox.pack_start(scrolled_window, True, True, 0)
        notebook = gtk.Notebook()
        # uncomment below to highlight tabs
        notebook.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(WHITE))
        notebook.set_tab_pos(gtk.POS_TOP)
        #notebook.set_default_size(400,400)
        notebook.show()
        lessonplans = {}
        lpdir = os.path.join(self.mdirpath,LANG[self.language]['lpdir'])
        lpentries = os.listdir(lpdir)
        for entry in lpentries:
            fpath = os.path.join(lpdir,entry)
            lessonplans[entry] = getwrappedfile(fpath,80)
        lpkeys = lessonplans.keys()
        lpkeys.sort()
        for lpkey in lpkeys:
            lpname = lpkey.replace('_',' ').replace('0','')[:-4]
            label = gtk.Label(lessonplans[lpkey])
            #if self.insugar:
            #    label.modify_fg(gtk.STATE_NORMAL,gtk.gdk.color_parse(WHITE))
            eb = gtk.EventBox()
            eb.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(WHITE))
            #label.set_line_wrap(True)
            label.show()
            eb.add(label)
            eb.show()
            #tlabel = gtk.Label('Lesson Plan %s' % str(i+1))
            tlabel = gtk.Label(lpname)
            tlabel.show()
            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            scrolled_window.show()
            scrolled_window.add_with_viewport(eb)
            notebook.append_page(scrolled_window, tlabel)
        #dia.action_area.pack_start(notebook, True, True, 0)
        dia.vbox.pack_start(notebook, True, True, 0)
        result = dia.run()
        dia.destroy()
    """

