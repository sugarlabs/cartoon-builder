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
#

### cartoonbuilder
###
### author: Ed Stoner (ed@whsd.net)
### (c) 2007 World Wide Workshop Foundation

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import logging
logger = logging.getLogger('cartoonbuilder')

#from gobject import SIGNAL_RUN_FIRST, TYPE_PYOBJECT

from toolkit.scrolledbox import VScrolledBox

import theme
import char
import ground
import sound
from document import Document, clean
from screenbuil import Screen
from utils import *

logger = logging.getLogger('cartoon-builder')


class View(Gtk.EventBox):
    __gsignals__ = {
        'frame-changed': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, 2 * [GObject.TYPE_PYOBJECT]),
        'ground-changed': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT]),
        'sound-changed': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [GObject.TYPE_PYOBJECT])}

    def set_frame(self, value):
        tape_num, frame = value

        if frame == None:
            clean(tape_num)
            self._tape[tape_num].get_child().set_from_pixbuf(theme.EMPTY_THUMB)

            if self._emission:
                self.emit('frame-changed', tape_num, None)
        else:
            if not frame.select():
                return False

            Document.tape[tape_num] = frame
            self._tape[tape_num].get_child().set_from_pixbuf(frame.thumb())

            if frame.custom():
                index = [i for i, f in enumerate(char.THEMES[-1].frames)
                        if f == frame][0]
                if index >= len(self._frames):
                    first = index / theme.FRAME_COLS * theme.FRAME_COLS
                    for i in range(first, first + theme.FRAME_COLS):
                        self._add_frame(i)

            if self._char.custom():
                self._frames[index].set_from_pixbuf(frame.thumb())

            if self._emission:
                self.emit('frame-changed', tape_num, frame)

        if self._tape_selected == tape_num:
            self._tape_cb(None, None, tape_num)

        return True

    def set_ground(self, value):
        self._set_combo(self._ground_combo, value)

    def set_sound(self, value):
        self._set_combo(self._sound_combo, value)

    def get_emittion(self):
        return self._emission

    def set_emittion(self, value):
        self._emission = value

    frame = GObject.property(type=object, getter=None, setter=set_frame)
    ground = GObject.property(type=object, getter=None, setter=set_ground)
    sound = GObject.property(type=object, getter=None, setter=set_sound)
    emittion = GObject.property(type=bool, default=True, getter=get_emittion,
            setter=set_emittion)

    def restore(self):
        def new_combo(themes, cb, object=None, closure=None):
            combo = ComboBox()
            sel = 0

            for i, o in enumerate(themes):
                if o:
                    combo.append_item(o, text=o.name,
                            size=(theme.THUMB_SIZE, theme.THUMB_SIZE),
                            pixbuf=o.thumb())
                    if object and o.name == object.name:
                        sel = i
                else:
                    combo.append_separator()

            combo.connect('changed', cb, closure)
            combo.set_active(sel)
            combo.show()

            return combo

        self.controlbox.pack_start(new_combo(char.THEMES, self._char_cb),
                False, False, 0)
        self._ground_combo = new_combo(ground.THEMES, self._combo_cb,
                Document.ground, self._ground_cb)
        self.controlbox.pack_start(self._ground_combo, False, False, 0)
        self._sound_combo = new_combo(sound.THEMES, self._combo_cb,
                Document.sound, self._sound_cb)
        self.controlbox.pack_start(self._sound_combo, False, False, 0)

        for i in range(theme.TAPE_COUNT):
            self._tape[i].get_child().set_from_pixbuf(Document.tape[i].thumb())
        self._tape_cb(None, None, 0)

    def play(self):
        self._play_tape_num = 0
        self._playing = GObject.timeout_add(self._delay, self._play_tape)

    def stop(self):
        self._playing = None
        self._screen.fgpixbuf = Document.tape[self._tape_selected].orig()
        self._screen.draw()

    def set_tempo(self, tempo):
        logger.debug('carto')
        logger.debug(tempo)
        self._delay = 10 + (10 - int(tempo)) * 100
        if self._playing:
            GObject.source_remove(self._playing)
            self._playing = GObject.timeout_add(self._delay, self._play_tape)

    def __init__(self):
        GObject.GObject.__init__(self)

        self._screen = Screen()
        self._play_tape_num = 0
        self._playing = None
        self._delay = 3 * 150
        self._tape_selected = -1
        self._tape = []
        self._char = None
        self._frames = []
        self._prev_combo_selected = {}
        self._emission = True
        self._screen_size_id = None

        # frames table

        self.table = Gtk.Table(  # theme.FRAME_ROWS, columns=theme.FRAME_COLS,
                homogeneous=False)

        for i in range(theme.FRAME_ROWS * theme.FRAME_COLS):
            self._add_frame(i)

        # frames box

        table_scroll = VScrolledBox()
        table_scroll.set_viewport(self.table)
        table_scroll.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BUTTON_BACKGROUND))

        yellow_frames = Gtk.EventBox()
        yellow_frames.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(YELLOW))
        table_frames = Gtk.EventBox()
        table_frames.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BACKGROUND))
        table_frames.set_border_width(5)
        table_frames.add(table_scroll)
        yellow_frames.add(table_frames)

        yelow_arrow = Gtk.Image()
        yelow_arrow.set_from_file(theme.path('icons', 'yellow_arrow.png'))

        frames_box = Gtk.VBox()
        frames_box.pack_start(yellow_frames, True, True, 0)
        frames_box.pack_start(yelow_arrow, False, False, 0)
        frames_box.props.border_width = theme.BORDER_WIDTH

        # screen

        screen_pink = Gtk.EventBox()
        screen_pink.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(PINK))
        screen_box = Gtk.EventBox()
        screen_box.set_border_width(5)
        screen_box.add(self._screen)
        screen_pink.add(screen_box)
        screen_pink.props.border_width = theme.BORDER_WIDTH

        # tape

        tape = Gtk.HBox()

        for i in range(TAPE_COUNT):
            frame_box = Gtk.VBox()

            filmstrip_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    theme.path('icons', 'filmstrip.png'), THUMB_SIZE, -1, False)

            filmstrip = Gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            frame_box.pack_start(filmstrip, False, False, 0)

            frame = Gtk.EventBox()
            frame.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            frame.connect('button_press_event', self._tape_cb, i)
            frame.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BLACK))
            frame.modify_bg(Gtk.StateType.PRELIGHT, Gdk.color_parse(BLACK))
            frame.props.border_width = 2
            frame.set_size_request(theme.THUMB_SIZE, theme.THUMB_SIZE)
            frame_box.pack_start(frame, True, True, 0)
            self._tape.append(frame)

            frame_image = Gtk.Image()
            frame_image.set_from_pixbuf(theme.EMPTY_THUMB)
            frame.add(frame_image)

            filmstrip = Gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            frame_box.pack_start(filmstrip, False, False, 0)

            tape.pack_start(frame_box, False, False, 0)

        # left control box

        self.controlbox = Gtk.VBox()
        self.controlbox.props.border_width = theme.BORDER_WIDTH
        self.controlbox.props.spacing = theme.BORDER_WIDTH

        leftbox = Gtk.VBox()
        logo = Gtk.Image()
        logo.set_from_file(theme.path('icons', 'logo.png'))
        leftbox.set_size_request(logo.props.pixbuf.get_width(), -1)
        leftbox.pack_start(logo, False, False, 0)
        leftbox.pack_start(self.controlbox, True, True, 0)

        # screen box

        screen_alignment = Gtk.Alignment.new(0.5, 0.5, 0, 0)
        screen_alignment.add(screen_pink)

        box = Gtk.EventBox()
        box.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BACKGROUND))
        box.connect('size-allocate', self._screen_size_cb, screen_pink)
        box.add(screen_alignment)

        cetralbox = Gtk.HBox()
        cetralbox.pack_start(box, expand=True, fill=True, padding=0)
        cetralbox.pack_start(frames_box, expand=False, fill=True, padding=0)

        hdesktop = Gtk.HBox()
        hdesktop.pack_start(leftbox, False, True, 0)
        hdesktop.pack_start(cetralbox, True, True, 0)

        # tape box

        arrow = Gtk.Image()
        arrow.set_from_file(theme.path('icons', 'pink_arrow.png'))
        tape_pink = Gtk.EventBox()
        tape_pink.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(PINK))
        tape_bg = Gtk.EventBox()
        tape_bg.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BACKGROUND))
        tape_bg.set_border_width(5)
        tape_bg.add(tape)
        tape_pink.add(tape_bg)

        tape_hbox = Gtk.HBox()
        tape_hbox.pack_start(tape_pink, True, False, 0)

        tape_box = Gtk.VBox()
        tape_box.props.border_width = theme.BORDER_WIDTH
        tape_box.pack_start(arrow, False, False, 0)
        tape_box.pack_start(tape_hbox, True, True, 0)

        desktop = Gtk.VBox()
        desktop.pack_start(hdesktop, True, True, 0)
        desktop.pack_start(tape_box, False, False, 0)

        greenbox = Gtk.EventBox()
        greenbox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BACKGROUND))
        greenbox.set_border_width(5)
        greenbox.add(desktop)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(YELLOW))
        self.add(greenbox)
        self.show_all()

    def _set_combo(self, combo, value):
        pos = -1

        for i, item in enumerate(combo.get_model()):
            if item[0] == value:
                pos = i
                break

        if pos == -1:
            combo.append_item(value, text=value.name,
                    size=(theme.THUMB_SIZE, theme.THUMB_SIZE),
                    pixbuf=value.thumb())
            pos = len(combo.get_model()) - 1

        combo.set_active(pos)

    def _play_tape(self):
        if not self._playing:
            return False

        self._screen.fgpixbuf = Document.tape[self._play_tape_num].orig()
        self._screen.draw()

        for i in range(theme.TAPE_COUNT):
            self._play_tape_num += 1
            if self._play_tape_num == TAPE_COUNT:
                self._play_tape_num = 0
            if Document.tape[self._play_tape_num].empty():
                continue
            return True

        return True

    def _add_frame(self, index):
        y = index / theme.FRAME_COLS
        x = index - y * theme.FRAME_COLS
        logger.debug('add new frame x=%d y=%d index=%d' % (x, y, index))

        image = Gtk.Image()
        image.show()
        image.set_from_pixbuf(theme.EMPTY_THUMB)
        self._frames.append(image)

        image_box = Gtk.EventBox()
        image_box.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        image_box.connect('button_press_event', self._frame_cb, index)
        image_box.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(BLACK))
        image_box.modify_bg(Gtk.StateType.PRELIGHT, Gdk.color_parse(BLACK))
        image_box.props.border_width = 2
        image_box.set_size_request(theme.THUMB_SIZE, theme.THUMB_SIZE)
        image_box.add(image)

        if self._char and self._char.custom():
            image_box.show()

        self.table.attach(image_box, x, x + 1, y, y + 1)

        return image

    def _tape_cb(self, widget, event, index):
        if event and event.button == 3:
            self.set_frame((index, None))
            return

        tape = self._tape[index]
        tape.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(YELLOW))
        tape.modify_bg(Gtk.StateType.PRELIGHT, Gdk.color_parse(YELLOW))

        if self._tape_selected != index:
            if self._tape_selected != -1:
                old_tape = self._tape[self._tape_selected]
                old_tape.modify_bg(Gtk.StateType.NORMAL,
                        Gdk.color_parse(BLACK))
                old_tape.modify_bg(Gtk.StateType.PRELIGHT,
                        Gdk.color_parse(BLACK))

        self._tape_selected = index
        self._screen.fgpixbuf = Document.tape[index].orig()
        self._screen.draw()

    def _frame_cb(self, widget, event, i):
        if event.button == 3:
            self._char.clean(i)
            self._frames[i].set_from_pixbuf(self._char.frames[i].thumb())
        else:
            if i < len(self._char.frames):
                frame = self._char.frames[i]
                if not self.set_frame((self._tape_selected, frame)):
                    return
            else:
                frame = None
                self.set_frame((self._tape_selected, None))

    def _char_cb(self, widget, closure):
        self._char = widget.props.value
        for i in range(len(self._frames)):
            if i < len(self._char.frames):
                self._frames[i].set_from_pixbuf(self._char.frames[i].thumb())
                self._frames[i].get_parent().show()
            else:
                self._frames[i].get_parent().hide()

    def _combo_cb(self, widget, cb):
        choice = widget.props.value.select()

        if not choice:
            widget.set_active(self._prev_combo_selected[widget])
            return

        if id(choice) != id(widget.props.value):
            widget.append_item(choice, text=choice.name,
                    size=(theme.THUMB_SIZE, theme.THUMB_SIZE),
                    pixbuf=choice.thumb())
            widget.set_active(len(widget.get_model()) - 1)

        self._prev_combo_selected[widget] = widget.get_active()
        cb(choice)

    def _ground_cb(self, choice):
        self._screen.bgpixbuf = choice.orig()
        self._screen.draw()
        Document.ground = choice
        if self._emission:
            self.emit('ground-changed', choice)

    def _sound_cb(self, choice):
        Document.sound = choice
        if self._emission:
            self.emit('sound-changed', choice)

    def _screen_size_cb(self, sender, aloc, widget):
        def set_size():
            size = min(aloc.width, aloc.height)
            widget.set_size_request(size, size)
            self._screen_size_id = None
            return False

        if self._screen_size_id is not None:
            GObject.source_remove(self._screen_size_id)
        self._screen_size_id = GObject.timeout_add(500, set_size)
