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

import theme
import char
import ground
import sound
from document import Document, clean
from utils import *

def play():
    View.play_tape_num = 0
    View.playing = gobject.timeout_add(View.delay, _play_tape)

def stop():
    View.playing = None

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
    class Screen(gtk.DrawingArea):
        def __init__(self):
            gtk.DrawingArea.__init__(self)
            self.gc = None  # initialized in realize-event handler
            self.width  = 0 # updated in size-allocate handler
            self.height = 0 # idem
            self.bgpixbuf = None
            self.fgpixbuf = None
            self.connect('size-allocate', self.on_size_allocate)
            self.connect('expose-event',  self.on_expose_event)
            self.connect('realize',       self.on_realize)

        def on_realize(self, widget):
            self.gc = widget.window.new_gc()
        
        def on_size_allocate(self, widget, allocation):
            self.height = self.width = min(allocation.width, allocation.height)
        
        def on_expose_event(self, widget, event):
            # This is where the drawing takes place
            if self.bgpixbuf:
                pixbuf = self.bgpixbuf
                if pixbuf.get_width != self.width:
                    pixbuf = theme.scale(pixbuf, self.width)
                widget.window.draw_pixbuf(self.gc, pixbuf, 0, 0, 0, 0, -1, -1, 0, 0)

            if self.fgpixbuf:
                pixbuf = self.fgpixbuf
                if pixbuf.get_width != self.width:
                    pixbuf = theme.scale(pixbuf, self.width)
                widget.window.draw_pixbuf(self.gc, pixbuf, 0, 0, 0, 0, -1, -1, 0, 0)

        def draw(self):
            self.queue_draw()

    screen = Screen()
    play_tape_num = 0
    playing = None
    delay = 3*150
    tape_selected = -1
    tape = []

    def __init__(self):
        gtk.EventBox.__init__(self)

        self._frames = []
        self._prev_combo_selected = {}

        # frames table

        self.table = gtk.Table(theme.FRAME_ROWS, columns=theme.FRAME_COLS,
                homogeneous=False)

        for y in range(theme.FRAME_ROWS):
            for x in range(theme.FRAME_COLS):
                image = gtk.Image()
                self._frames.append(image)

                image_box = gtk.EventBox()
                image_box.set_events(gtk.gdk.BUTTON_PRESS_MASK)
                image_box.connect('button_press_event', self._frame_cb,
                        y * theme.FRAME_COLS + x)
                image_box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLACK))
                image_box.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(BLACK))
                image_box.props.border_width = 2
                image_box.set_size_request(theme.THUMB_SIZE, theme.THUMB_SIZE)
                image_box.add(image)

                self.table.attach(image_box, x, x+1, y, y+1)

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
        screen_box.add(self.screen)
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
        self.controlbox.pack_start(new_combo(ground.THEMES, self._combo_cb,
                Document.ground, self._ground_cb), False, False)
        self.controlbox.pack_start(new_combo(sound.THEMES, self._combo_cb,
                Document.sound, self._sound_cb), False, False)

        for i in range(theme.TAPE_COUNT):
            View.tape[i].child.set_from_pixbuf(Document.tape[i].thumb())
        self._tape_cb(None, None, 0)

        return False

    def _tape_cb(self, widget, event, index):
        if event and event.button == 3:
            clean(index)
            View.tape[index].child.set_from_pixbuf(theme.EMPTY_THUMB)

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
        self.screen.fgpixbuf = Document.tape[index].orig()
        self.screen.draw()

    def _frame_cb(self, widget, event, i):

        if event.button == 3:
            self.char.clean(i)
            self._frames[i].set_from_pixbuf(self.char.frames[i].thumb())
        else:
            frame = self.char.frames[i]
            if frame.select():
                Document.tape[View.tape_selected] = frame
                View.tape[View.tape_selected].child.set_from_pixbuf(frame.thumb())
                self._frames[i].set_from_pixbuf(frame.thumb())
                self._tape_cb(None, None, View.tape_selected)

    def _char_cb(self, widget, closure):
        self.char = widget.props.value
        for i in range(len(self._frames)):
            self._frames[i].set_from_pixbuf(self.char.frames[i].thumb())

    def _combo_cb(self, widget, cb):
        choice = widget.props.value.select()

        if not choice:
            widget.set_active(self._prev_combo_selected[widget])
            return

        if id(choice) != id(widget.props.value):
            pos = widget.get_active()
            widget.append_item(choice, text = choice.name,
                    size = (theme.THUMB_SIZE, theme.THUMB_SIZE),
                    pixbuf = choice.thumb(), position = pos)
            widget.set_active(pos)

        self._prev_combo_selected[widget] = widget.get_active()
        cb(choice)

    def _ground_cb(self, choice):
        self.screen.bgpixbuf = choice.orig()
        self.screen.draw()
        Document.ground = choice

    def _sound_cb(self, choice):
        Document.sound = choice

    def _screen_size_cb(self, widget, aloc):
        size = min(aloc.width, aloc.height)
        widget.child.set_size_request(size, size)
