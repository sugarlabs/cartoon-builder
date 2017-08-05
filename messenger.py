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

import logging
import dbus
from dbus.gobject_service import ExportedGObject
from dbus.service import method, signal

import toolkit.json as json
from sugar3.presence import presenceservice

import char
import ground
import sound
from document import Document

logger = logging.getLogger('cartoon-builder')

SERVICE = 'org.sugarlabs.CartoonBuilder'
IFACE = SERVICE
PATH = '/org/sugarlabs/CartoonBuilder'


class Slot:
    def __init__(self, sender=None, raw=None):
        if sender:
            data = json.loads(raw)
            self.seqno = data['seqno']
            self.oid = data['oid']
            self.sender = sender
        else:
            self.seqno = -1
            self.oid = None
            self.sender = None

    def serialize(self):
        return json.dumps({
            'seqno': self.seqno,
            'oid': self.oid})


class Messenger(ExportedGObject):
    def __init__(self, tube, initiator, view):
        ExportedGObject.__init__(self, tube, PATH)

        self.initiator = initiator
        self._tube = tube
        self._entered = False
        self._slots = {}
        self._view = view

        self._view.connect('frame-changed', self._frame_changed_cb)
        self._view.connect('ground-changed', self._ground_changed_cb)
        self._view.connect('sound-changed', self._sound_changed_cb)
        self._tube.watch_participants(self._participant_change_cb)

    def _participant_change_cb(self, added, removed):
        if not self._entered and added:
            self.me = self._tube.get_unique_name()

            slots = [('%s:%d' % (FRAME, i), f) \
                    for i, f in enumerate(Document.tape)] + \
                            [(GROUND, Document.ground), (SOUND, Document.sound)]
            for i in slots:
                self._slots[i[0]] = Slot()

            if self.initiator:
                self._tube.add_signal_receiver(self._ping_cb, '_ping', IFACE,
                        path=PATH, sender_keyword='sender')
                for i in slots:
                    slot = self._slots[i[0]]
                    slot.seqno = 0
                    slot.oid = i[1].id
                    slot.sender = self.me
            else:
                self._pong_handle = self._tube.add_signal_receiver(
                        self._pong_cb, '_pong', IFACE, path=PATH,
                        sender_keyword='sender')
                self._ping()

            self._tube.add_signal_receiver(self._notify_cb, '_notify', IFACE,
                    path=PATH, sender_keyword='sender')
            self._entered = True

    # incomers' signal to retrieve initial snapshot
    @signal(IFACE, signature='')
    def _ping(self):
        logger.debug('send ping')
        pass

    # object is ready to post snapshot to incomer
    @signal(IFACE, signature='')
    def _pong(self):
        logger.debug('send pong')
        pass

    # slot was changed
    @signal(IFACE, signature='ss')
    def _notify(self, slot, raw):
        pass

    # the whole list of slots for incomers
    @method(dbus_interface=IFACE, in_signature='', out_signature='a{ss}',
            sender_keyword='sender')
    def _snapshot(self, sender=None):
        logger.debug('_snapshot requested from %s' % sender)
        out = {}

        for i, slot in self._slots.items():
            out[i] = slot.serialize()

        return out

    # fetch content of specified object
    @method(dbus_interface=IFACE, in_signature='ss', out_signature='say',
            sender_keyword='sender', byte_arrays=True)
    def _fetch(self, type, oid, sender=None):
        logger.debug('_fetch requested from %s type=%s oid=%s' \
                % (sender, type, oid))
        return object_serialize(type, oid)

    def _ping_cb(self, sender=None):
        if sender == self.me:
            return
        logger.debug('_ping received from %s' % sender)
        self._pong()

    def _pong_cb(self, sender=None):
        if sender == self.me:
            return
        logger.debug('_pong sent from %s' % sender)

        # we've got source for _snapshot and don't need _pong anymore
        self._tube.remove_signal_receiver(self._pong_handle)
        self._pong_handle = None

        remote = self._tube.get_object(sender, PATH)
        rawlist = remote._snapshot()

        logger.debug('snapshot received len=%d' % len(rawlist))

        for slot, raw in rawlist.items():
            self._receive(slot, raw, sender)

        # we are ready to receive _snapshot requests
        self._tube.add_signal_receiver(self._ping_cb, '_ping', IFACE,
                path=PATH, sender_keyword='sender')

    def _notify_cb(self, slot, raw, sender=None):
        if sender == self.me:
            return
        logger.debug('_notify requested from %s' % sender)
        self._receive(slot, raw, sender)

    def _receive(self, slot, raw, sender):
        cur = self._slots[slot]
        new = Slot(sender, raw)

        logger.debug('object received slot=%s seqno=%d sender=%s oid=%s from %s'
                % (slot, new.seqno, new.sender, new.oid, sender))

        if cur.seqno > new.seqno:
            logger.debug('trying to rewrite newer value by older one')
            return
        elif cur.seqno == new.seqno:
            # arrived value was sent at the same time as current one
            if cur.sender > sender:
                logger.debug('current value is higher ranked then arrived')
                return
            if cur.sender == self.me:
                # we sent current and arrived value rewrites it
                logger.debug('resend current with higher seqno')
                self._send(slot, cur.oid)
                return
            else:
                logger.debug('just discard low rank')
                return
        else:
            logger.debug('accept higher seqno')

        if new.oid and not object_find(slot, new.oid):
            remote = self._tube.get_object(sender, PATH)
            name, raw = remote._fetch(slot, new.oid, byte_arrays=True)
            object_new(slot, new.oid, name, raw)

        object_select(self._view, slot, new.oid)
        self._slots[slot] = new

    def _send(self, slot_num, oid):
        slot = self._slots[slot_num]
        slot.seqno += 1
        slot.sender = self.me
        slot.oid = oid
        self._notify(slot_num, slot.serialize())

        logger.debug('_send slot=%s oid=%s seqno=%d'
                % (slot_num, oid, slot.seqno))

    def _frame_changed_cb(self, sender, index, frame):
        self._send('%s:%d' % (FRAME, index), frame and frame.id)

    def _ground_changed_cb(self, sender, ground):
        self._send(GROUND, ground.id)

    def _sound_changed_cb(self, sender, sound):
        self._send(SOUND, sound.id)


FRAME = 'frame'
GROUND = 'ground'
SOUND = 'sound'

OBJECTS = {
    FRAME: char.THEMES[-1].frames,
    GROUND: ground.THEMES,
    SOUND: sound.THEMES}


def object_find(type, oid):
    if type.startswith(FRAME):
        for c in char.THEMES:
            if not c:
                continue
            for i in c.frames:
                if i.id == oid:
                    return i
    else:
        for i in OBJECTS[type.split(':')[0]]:
            if i and i.id == oid:
                return i
    return None


def object_new(type, oid, name, raw):
    logger.debug('add new object type=%s oid=%s' % (type, oid))

    if type.startswith(FRAME):
        object = char.RestoredFrame(oid, raw)
        for i, frame in enumerate(OBJECTS[FRAME]):
            if not frame.id:
                OBJECTS[FRAME][i] = object
                return
    elif type.startswith(GROUND):
        object = ground.RestoredGround(name, oid, raw)
    elif type.startswith(SOUND):
        object = sound.RestoredSound(name, oid, raw)
    else:
        logger.error('cannot create object of type %s' % type)
        return

    OBJECTS[type.split(':')[0]].append(object)


def object_serialize(type, oid):
    object = object_find(type, oid)

    if object:
        return (object.name, object.serialize())
    else:
        logger.error('cannot find object to serialize type=%s oid=%s' \
                % (type, oid))
        return ('', '')


def object_select(view, type, oid):
    if oid:
        object = object_find(type, oid)
    else:
        object = None

    try:
        view.props.emittion = False

        if type.startswith(FRAME):
            index = int(type.split(':')[1])
            view.props.frame = (index, object)
        elif type.startswith(GROUND):
            view.props.ground = object
        elif type.startswith(SOUND):
            view.props.sound = object
        else:
            logger.error('cannot find object to select type=%s oid=%s' % (type, oid))
    finally:
        view.props.emittion = True
