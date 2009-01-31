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

from sugar.activity import activity
from sugar.presence import presenceservice
from sugar.presence.tubeconn import TubeConnection
import telepathy
import telepathy.client
from dbus import Interface
from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject
from gettext import gettext as _

from sugar.activity.activity import get_activity_root

from View import View
from Toolbar import *
import Document
import Char
import Ground
import Sound

SERVICE = 'org.freedesktop.Telepathy.Tube.Connect'
IFACE = SERVICE
PATH = '/org/freedesktop/Telepathy/Tube/Connect'

TMPDIR = os.path.join(get_activity_root(), 'tmp')

class CartoonBuilderActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self,handle)

        self.app = View()
        toolbox = activity.ActivityToolbox(self)
        self.set_toolbox(toolbox)
        toolbox.show()
        self.set_canvas(self.app.main)

        """
        # mesh stuff
        self.pservice = presenceservice.get_instance()
        owner = self.pservice.get_owner()
        self.owner = owner
        try:
            name, path = self.pservice.get_preferred_connection()
            self.tp_conn_name = name
            self.tp_conn_path = path
            self.conn = telepathy.client.Connection(name, path)
        except TypeError:
            pass
        self.initiating = None

        #sharing stuff
        self.game = None
        self.connect('shared', self._shared_cb)
        if self._shared_activity:
            # we are joining the activity
            self.connect('joined', self._joined_cb)
            if self.get_shared():
                # oh, OK, we've already joined
                self._joined_cb()
        else:
            # we are creating the activity
            pass
        """

    def read_file(self, filepath):
        Document.load(filepath)
        Char.load()
        Ground.load()
        Sound.load()

    def write_file(self, filepath):
        Document.save(filepath)


    def _shared_cb(self,activity):
        self.initiating = True
        self._setup()
        id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
              SERVICE, {})
        #self.app.export.set_label('Shared Me')

    def _joined_cb(self,activity):
        if self.game is not None:
            return

        if not self._shared_activity:
            return

        #for buddy in self._shared_activity.get_joined_buddies():
        #    self.buddies_panel.add_watcher(buddy)

        #logger.debug('Joined an existing Connect game')
        #self.app.export.set_label('Joined You')
        self.initiating = False
        self._setup()

        #logger.debug('This is not my activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb,
            error_handler=self._list_tubes_error_cb)

    def _setup(self):
        if self._shared_activity is None:
            return

        bus_name, conn_path, channel_paths = self._shared_activity.get_channels()

        # Work out what our room is called and whether we have Tubes already
        room = None
        tubes_chan = None
        text_chan = None
        for channel_path in channel_paths:
            channel = telepathy.client.Channel(bus_name, channel_path)
            htype, handle = channel.GetHandle()
            if htype == telepathy.HANDLE_TYPE_ROOM:
                #logger.debug('Found our room: it has handle#%d "%s"',
                #    handle, self.conn.InspectHandles(htype, [handle])[0])
                room = handle
                ctype = channel.GetChannelType()
                if ctype == telepathy.CHANNEL_TYPE_TUBES:
                    #logger.debug('Found our Tubes channel at %s', channel_path)
                    tubes_chan = channel
                elif ctype == telepathy.CHANNEL_TYPE_TEXT:
                    #logger.debug('Found our Text channel at %s', channel_path)
                    text_chan = channel

        if room is None:
            #logger.error("Presence service didn't create a room")
            return
        if text_chan is None:
            #logger.error("Presence service didn't create a text channel")
            return

        # Make sure we have a Tubes channel - PS doesn't yet provide one
        if tubes_chan is None:
            #logger.debug("Didn't find our Tubes channel, requesting one...")
            tubes_chan = self.conn.request_channel(telepathy.CHANNEL_TYPE_TUBES,
                telepathy.HANDLE_TYPE_ROOM, room, True)

        self.tubes_chan = tubes_chan
        self.text_chan = text_chan

        tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal('NewTube',
            self._new_tube_cb)

    def _list_tubes_reply_cb(self, tubes):
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        #logger.error('ListTubes() failed: %s', e)
        pass

    def _new_tube_cb(self, id, initiator, type, service, params, state):
        #logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
        #             'params=%r state=%d', id, initiator, type, service,
        #             params, state)

        if (self.game is None and type == telepathy.TUBE_TYPE_DBUS and
            service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)

            tube_conn = TubeConnection(self.conn,
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES],
                id, group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])
            self.game = ConnectGame(tube_conn, self.initiating, self)

class ConnectGame(ExportedGObject):
    def __init__(self,tube, is_initiator, activity):
        super(ConnectGame,self).__init__(tube,PATH)
        self.tube = tube
        self.is_initiator = is_initiator
        self.entered = False
        self.activity = activity

        self.ordered_bus_names=[]
        self.tube.watch_participants(self.participant_change_cb)

    def participant_change_cb(self, added, removed):
        if not self.entered:
            if self.is_initiator:
                self.add_hello_handler()
            else:
                self.Hello()
        self.entered = True

    @signal(dbus_interface=IFACE,signature='')
    def Hello(self):
        """Request that this player's Welcome method is called to bring it
        up to date with the game state.
        """

    @method(dbus_interface=IFACE, in_signature='s', out_signature='')
    def Welcome(self, sdata):
        #sdata is the zip file contents
        #self.activity.app.lessonplans.set_label('got data to restore')
        self.activity.app.restore(str(sdata))

    def add_hello_handler(self):
        self.tube.add_signal_receiver(self.hello_cb, 'Hello', IFACE,
            path=PATH, sender_keyword='sender')

    def hello_cb(self, sender=None):
        self.tube.get_object(sender, PATH).Welcome(self.activity.app.getsdata(),dbus_interface=IFACE)

"""
    def getsdata(self):
        #self.lessonplans.set_label('getting sdata')
        # THE BELOW SHOULD WORK BUT DOESN'T
        #zf = StringIO.StringIO()
        #self.savetozip(zf)
        #zf.seek(0)
        #sdata = zf.read()
        #zf.close()
        # END OF STUFF THAT DOESN'T WORK
        sdd = {}
        tmpbgpath = os.path.join(TMPDIR,'back.png')
        self.bgpixbuf.save(tmpbgpath,'png')
        sdd['pngdata'] = file(tmpbgpath).read()
        os.remove(tmpbgpath)
        sdd['fgpixbufpaths'] = self.fgpixbufpaths
        #sdd['fgpixbufs'] = []
        #count = 1
        #for pixbuf in self.fgpixbufs:
        #    filename = '%02d.png' % count
        #    filepath = os.path.join(TMPDIR,filename)
        #    pixbuf.save(filepath,'png')
        #    sdd['fgpixbufs'].append(file(filepath).read())
        #    os.remove(filepath)
        #    count += 1
        return pickle.dumps(sdd)
"""
