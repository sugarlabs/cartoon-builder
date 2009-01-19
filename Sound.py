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

Size = (100, 100)

class Sound:
    id = 0
    pixbuf = None #gtk.gdk.Pixbuf()

def themes():
    return [Sound()]

def play():
    if self.soundfile:
        #self.player.set_property('uri', 'file://' + self.soundfile)
        self.player.set_state(gst.STATE_PLAYING)

def stop():
    if self.soundfile:
        self.player.set_state(gst.STATE_NULL)

def switch(id):
    self.soundfile = self.sounds[self.soundindex]

    if self.soundfile:
        soundname = os.path.splitext(os.path.split(self.soundfile)[1])[0]
        self.player.set_property('uri', 'file://' + self.soundfile)
        if self.playing:
            self.player.set_state(gst.STATE_NULL)
            self.player.set_state(gst.STATE_PLAYING)
    else:
        soundname = 'No Sound'
        if self.playing:
            self.player.set_state(gst.STATE_NULL)
    self.soundlabel.set_text(soundname.capitalize())


def on_gstmessage(self, bus, message):
    t = message.type
    if t == gst.MESSAGE_EOS:
        # END OF SOUND FILE
        self.player.set_state(gst.STATE_NULL)
        self.player.set_state(gst.STATE_PLAYING)
    elif t == gst.MESSAGE_ERROR:
        self.player.set_state(gst.STATE_NULL)

def init():
    self.sounds = ['']
    soundfile = file(os.path.join(self.mdirpath,'config.sounds'))
    for line in soundfile:
        soundfilepath = line.strip()
        if soundfilepath[0] != '/':
            soundfilepath = os.path.join(self.mdirpath,line.strip())
        if os.path.isfile(soundfilepath):
            self.sounds.append(soundfilepath)
    soundfile.close()

    self.soundfile = self.sounds[self.soundindex]

    # START GSTREAMER STUFF
    self.player = gst.element_factory_make("playbin", "player")
    fakesink = gst.element_factory_make('fakesink', "my-fakesink")
    self.player.set_property("video-sink", fakesink)
    self.bus = self.player.get_bus()
    self.bus.add_signal_watch()
    self.bus.connect('message', self.on_gstmessage)
    # END GSTREAMER STUFF

