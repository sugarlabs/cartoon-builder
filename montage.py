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

import gtk
import gobject
import logging
from gobject import SIGNAL_RUN_FIRST, TYPE_PYOBJECT

import theme
import char
import ground
import sound
from document import Document, clean
from screen import Screen
from utils import *

logger = logging.getLogger('cartoon-builder')

def play():
    View.play_tape_num = 0
    View.playing = gobject.timeout_add(View.delay, _play_tape)

def stop():
    View.playing = None
    View.screen.fgpixbuf = Document.tape[View.tape_selected].orig()
    View.screen.draw()

def set_tempo(tempo):
    View.delay = 10 + (10-int(tempo)) * 100
    if View.playing:
        gobject.source_remove(View.playing)
        View.playing = gobject.timeout_add(View.delay, _play_tape)

def clear_tape():
    for i in range(TAPE_COUNT):
        clean(i)
        View.tape[i].child.set_from_pixbuf(theme.EMPTY_THUMB)

    View.screen.fgpixbuf = Document.tape[View.tape_selected].orig()
    View.screen.draw()

def _play_tape():
    if not View.playing:
        return False

    View.screen.fgpixbuf = Document.tape[View.play_tape_num].orig()
    View.screen.draw()

    for i in range(theme.TAPE_COUNT):
        View.play_tape_num += 1
        if View.play_tape_num == TAPE_COUNT:
            View.play_tape_num = 0
        if Document.tape[View.play_tape_num].empty():
            continue
        return True

    return True

class View(gtk.EventBox):
    __gsignals__ = {
        'frame-changed' : (SIGNAL_RUN_FIRST, None, 2*[TYPE_PYOBJECT]), 
        'ground-changed': (SIGNAL_RUN_FIRST, None, [TYPE_PYOBJECT]), 
        'sound-changed' : (SIGNAL_RUN_FIRST, None, [TYPE_PYOBJECT]) } 

    screen = Screen()
    play_tape_num = 0
    playing = None
    delay = 3*150
    tape_selected = -1
    tape = []

    def set_frame(self, value):
        tape_num, frame = value

        if frame == None:
            clean(tape_num)
            View.tape[tape_num].child.set_from_pixbuf(theme.EMPTY_THUMB)
        else:
            if not frame.select():
                return False

            Document.tape[tape_num] = frame
            View.tape[tape_num].child.set_from_pixbuf(frame.thumb())

            if frame.custom():
                index = [i for i, f in enumerate(char.THEMES[-1].frames)
                        if f == frame][0]
                if index >= len(self._frames):
                    first = index / theme.FRAME_COLS * theme.FRAME_COLS
                    for i in range(first, first + theme.FRAME_COLS):
                        self._add_frame(i)

            if self.char.custom():
                self._frames[index].set_from_pixbuf(frame.thumb())

        if View.tape_selected == tape_num:
            self._tape_cb(None, None, tape_num)

        return True

    def set_ground(self, value):
        self._set_combo(self._ground_combo, value)

    def set_sound(self, value):
        self._set_combo(self._sound_combo, value)

    def _set_combo(self, combo, value):
        try:
            self._stop_emission = True
            pos = -1

            for i, item in enumerate(combo.get_model()):
                if item[0] == value:
                    pos = i
                    break

            if pos == -1:
                combo.append_item(value, text = value.name,
                        size = (theme.THUMB_SIZE, theme.THUMB_SIZE),
                        pixbuf = value.thumb())
                pos = len(combo.get_model())-1

            combo.set_active(pos)
        finally:
            self._stop_emission = False

    frame = gobject.property(type=object, getter=None, setter=set_frame)
    ground = gobject.property(type=object, getter=None, setter=set_ground)
    sound = gobject.property(type=object, getter=None, setter=set_sound)

    def restore(self):
        def new_combo(themes, cb, object = None, closure = None):
            combo = ComboBox()
            sel = 0

            for i, o in enumerate(themes):
                if o:
                    combo.append_item(o, text = o.name,
                            size = (theme.THUMB_SIZE, theme.THUMB_SIZE),
                            pixbuf = o.thumb())
                    if object and o.name == object.name:
                        sel = i
                else:
                    combo.append_separator()

            combo.connect('changed', cb, closure)
            combo.set_active(sel)
            combo.show()

            return combo

        self.controlbox.pack_start(new_combo(char.THEMES, self._char_cb),
                False, False)
        self._ground_combo =  new_combo(ground.THEMES, self._combo_cb,
                Document.ground, self._ground_cb)
        self.controlbox.pack_start(self._ground_combo, False, False)
        self._sound_combo = new_combo(sound.THEMES, self._combo_cb,
                Document.sound, self._sound_cb)
        self.controlbox.pack_start(self._sound_combo, False, False)

        for i in range(theme.TAPE_COUNT):
            View.tape[i].child.set_from_pixbuf(Document.tape[i].thumb())
        self._tape_cb(None, None, 0)

        return False

    def __init__(self):
        gtk.EventBox.__init__(self)

        self.char = None
        self._frames = []
        self._prev_combo_selected = {}
        self._stop_emission = False

        # frames table

        self.table = gtk.Table(#theme.FRAME_ROWS, columns=theme.FRAME_COLS,
                homogeneous=False)

        for i in range(theme.FRAME_ROWS * theme.FRAME_COLS):
            self._add_frame(i)

        # frames box

        table_scroll = VScrolledBox()
        table_scroll.set_viewport(self.table)
        table_scroll.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BUTTON_BACKGROUND))

        yellow_frames = gtk.EventBox()
        yellow_frames.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        table_frames = gtk.EventBox()
        table_frames.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        table_frames.set_border_width(5)
        table_frames.add(table_scroll)
        yellow_frames.add(table_frames)

        yelow_arrow = gtk.Image()
        yelow_arrow.set_from_file(theme.path('icons', 'yellow_arrow.png'))

        frames_box = gtk.VBox()
        frames_box.pack_start(yellow_frames, True, True)
        frames_box.pack_start(yelow_arrow, False, False)
        frames_box.props.border_width = theme.BORDER_WIDTH

        # screen

        screen_pink = gtk.EventBox()
        screen_pink.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
        screen_box = gtk.EventBox()
        screen_box.set_border_width(5)
        screen_box.add(View.screen)
        screen_pink.add(screen_box)
        screen_pink.props.border_width = theme.BORDER_WIDTH

        # tape

        tape = gtk.HBox()

        for i in range(TAPE_COUNT):
            frame_box = gtk.VBox()

            filmstrip_pixbuf = gtk.gdk.pixbuf_new_from_file_at_scale(
                    theme.path('icons', 'filmstrip.png'), THUMB_SIZE, -1, False)

            filmstrip = gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            frame_box.pack_start(filmstrip, False, False)

            frame = gtk.EventBox()
            frame.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            frame.connect('button_press_event', self._tape_cb, i)
            frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLACK))
            frame.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(BLACK))
            frame.props.border_width = 2
            frame.set_size_request(theme.THUMB_SIZE, theme.THUMB_SIZE)
            frame_box.pack_start(frame)
            View.tape.append(frame)

            frame_image = gtk.Image()
            frame_image.set_from_pixbuf(theme.EMPTY_THUMB)
            frame.add(frame_image)

            filmstrip = gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            frame_box.pack_start(filmstrip, False, False)

            tape.pack_start(frame_box, False, False)

        # left control box
        
        self.controlbox = gtk.VBox()
        self.controlbox.props.border_width = theme.BORDER_WIDTH
        self.controlbox.props.spacing = theme.BORDER_WIDTH

        leftbox = gtk.VBox()
        logo = gtk.Image()
        logo.set_from_file(theme.path('icons', 'logo.png'))
        leftbox.set_size_request(logo.props.pixbuf.get_width(), -1)
        leftbox.pack_start(logo, False, False)
        leftbox.pack_start(self.controlbox, True, True)
        
        # screen box

        screen_alignment = gtk.Alignment(0.5, 0.5, 0, 0)
        screen_alignment.add(screen_pink)
        screen_alignment.connect('size-allocate', self._screen_size_cb)

        cetralbox = gtk.HBox()
        cetralbox.pack_start(screen_alignment, True, True)
        cetralbox.pack_start(frames_box, True, False)

        hdesktop = gtk.HBox()
        hdesktop.pack_start(leftbox,False,True,0)
        hdesktop.pack_start(cetralbox,True,True,0)

        # tape box

        arrow = gtk.Image()
        arrow.set_from_file(theme.path('icons', 'pink_arrow.png'))
        tape_pink = gtk.EventBox()
        tape_pink.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(PINK))
        tape_bg = gtk.EventBox()
        tape_bg.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BACKGROUND))
        tape_bg.set_border_width(5)
        tape_bg.add(tape)
        tape_pink.add(tape_bg)

        tape_hbox = gtk.HBox()
        tape_hbox.pack_start(tape_pink, True, False)

        tape_box = gtk.VBox()
        tape_box.props.border_width = theme.BORDER_WIDTH
        tape_box.pack_start(arrow, False, False)
        tape_box.pack_start(tape_hbox)

        desktop = gtk.VBox()
        desktop.pack_start(hdesktop,True,True,0)
        desktop.pack_start(tape_box, False, False, 0)

        greenbox = gtk.EventBox()
        greenbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        greenbox.set_border_width(5)
        greenbox.add(desktop)

        self.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        self.add(greenbox)
        self.show_all()

    def _add_frame(self, index):
        y = index / theme.FRAME_COLS
        x = index - y*theme.FRAME_COLS
        logger.debug('add new frame x=%d y=%d index=%d' % (x, y, index))

        image = gtk.Image()
        image.show()
        image.set_from_pixbuf(theme.EMPTY_THUMB)
        self._frames.append(image)

        image_box = gtk.EventBox()
        image_box.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        image_box.connect('button_press_event', self._frame_cb, index)
        image_box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLACK))
        image_box.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(BLACK))
        image_box.props.border_width = 2
        image_box.set_size_request(theme.THUMB_SIZE, theme.THUMB_SIZE)
        image_box.add(image)

        if self.char and self.char.custom():
            image_box.show()

        self.table.attach(image_box, x, x+1, y, y+1)

        return image

    def _tape_cb(self, widget, event, index):
        if event and event.button == 3:
            self.set_frame((index, None))
            self.emit('frame-changed', index, None)
            return

        tape = View.tape[index]
        tape.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(YELLOW))
        tape.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(YELLOW))

        if View.tape_selected != index:
            if View.tape_selected != -1:
                old_tape = View.tape[View.tape_selected]
                old_tape.modify_bg(gtk.STATE_NORMAL,
                        gtk.gdk.color_parse(BLACK))
                old_tape.modify_bg(gtk.STATE_PRELIGHT,
                        gtk.gdk.color_parse(BLACK))

        View.tape_selected = index
        View.screen.fgpixbuf = Document.tape[index].orig()
        View.screen.draw()

    def _frame_cb(self, widget, event, i):
        if event.button == 3:
            self.char.clean(i)
            self._frames[i].set_from_pixbuf(self.char.frames[i].thumb())
        else:
            if i < len(self.char.frames):
                frame = self.char.frames[i]
                if not self.set_frame((View.tape_selected, frame)):
                    return
            else:
                frame = None
                self.set_frame((View.tape_selected, None))

            self.emit('frame-changed', View.tape_selected, frame)

    def _char_cb(self, widget, closure):
        self.char = widget.props.value
        for i in range(len(self._frames)):
            if i < len(self.char.frames):
                self._frames[i].set_from_pixbuf(self.char.frames[i].thumb())
                self._frames[i].parent.show()
            else:
                self._frames[i].parent.hide()

    def _combo_cb(self, widget, cb):
        choice = widget.props.value.select()

        if not choice:
            widget.set_active(self._prev_combo_selected[widget])
            return

        if id(choice) != id(widget.props.value):
            widget.append_item(choice, text = choice.name,
                    size = (theme.THUMB_SIZE, theme.THUMB_SIZE),
                    pixbuf = choice.thumb())
            widget.set_active(len(widget.get_model())-1)

        self._prev_combo_selected[widget] = widget.get_active()
        cb(choice)

    def _ground_cb(self, choice):
        View.screen.bgpixbuf = choice.orig()
        View.screen.draw()
        Document.ground = choice
        if not self._stop_emission:
            self.emit('ground-changed', choice)

    def _sound_cb(self, choice):
        Document.sound = choice
        if not self._stop_emission:
            self.emit('sound-changed', choice)

    def _screen_size_cb(self, widget, aloc):
        size = min(aloc.width, aloc.height)
        widget.child.set_size_request(size, size)
