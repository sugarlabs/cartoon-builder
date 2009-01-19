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
from sugar.graphics.objectchooser import ObjectChooser

import Sound

class Toolbar(gtk.Toolbar):
    def __init__(self, activity, app):
        gtk.Toolbar.__init__(self)
        self.activity = activity
        self.app = app

        self.playButton = ToggleToolButton('media-playback-start')
        self.playButton.connect('toggled', self._playButton_cb)
        self.insert(self.playButton, -1)
        self.playButton.show()
        self.playButton.set_tooltip(_('Play / Pause'))

        #Play button Image
        self.playButtonImg = gtk.Image()
        self.playButtonImg.set_from_icon_name('media-playback-start', gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.playButtonImg.show()

        #Pause button Image
        self.pauseButtonImg = gtk.Image()
        self.pauseButtonImg.set_from_icon_name('media-playback-pause', gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.pauseButtonImg.show()

    def _playButton_cb(self, widget):
        if widget.get_active():
            widget.set_icon_widget(self.pauseButtonImg)
            Sound.play()
            self.app.play()
        else:
            widget.set_icon_widget(self.playButtonImg)
            Sound.stop()
            self.app.stop()


"""
    def image_cb(self, button):
        chooser = ObjectChooser('Choose Image',self.activity,
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        try:
            result = chooser.run()
            if result == gtk.RESPONSE_ACCEPT:
                jobject = chooser.get_selected_object()
                if jobject and jobject.file_path:
                    self.app.setback(jobject.file_path)
        finally:
            chooser.destroy()
            del chooser
"""
