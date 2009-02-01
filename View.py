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

import time
import pygtk
import gtk
import gobject
import gettext
import os
import textwrap

import Theme
import Char
import Ground
import Sound
from Document import Document
from Utils import *

class FrameWidget(gtk.DrawingArea):
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
                pixbuf = Theme.scale(pixbuf, self.width)
            widget.window.draw_pixbuf(self.gc, pixbuf, 0, 0, 0, 0, -1, -1, 0, 0)

        if self.fgpixbuf:
            pixbuf = self.fgpixbuf
            if pixbuf.get_width != self.width:
                pixbuf = Theme.scale(pixbuf, self.width)
            widget.window.draw_pixbuf(self.gc, pixbuf, 0, 0, 0, 0, -1, -1, 0, 0)

    def draw(self):
        self.queue_draw()

class View:
    def __init__(self):
        self._playing = None
        self.waittime = 3*150
        self.tape = []
        self.frames = []
        self._prev_combo_selected = {}

        # frames table

        from math import ceil

        rows = max((DESKTOP_HEIGHT - THUMB_SIZE*3) / THUMB_SIZE,
                int(ceil(float(FRAME_COUNT) / FRAME_COLS)))

        self.table = gtk.Table(rows, columns=Theme.FRAME_COLS, homogeneous=False)

        for y in range(rows):
            for x in range(Theme.FRAME_COLS):
                image = gtk.Image()
                self.frames.append(image)

                image_box = gtk.EventBox()
                image_box.set_events(gtk.gdk.BUTTON_PRESS_MASK)
                image_box.connect('button_press_event', self._frame_cb,
                        y * Theme.FRAME_COLS + x)
                image_box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLACK))
                image_box.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(BLACK))
                image_box.props.border_width = 2
                image_box.set_size_request(Theme.THUMB_SIZE, Theme.THUMB_SIZE)
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
        yelow_arrow.set_from_file(Theme.path('icons/yellow_arrow.png'))

        frames_box = gtk.VBox()
        frames_box.pack_start(yellow_frames, True, True)
        frames_box.pack_start(yelow_arrow, False, False)
        frames_box.props.border_width = 20

        # screen

        self.screen = FrameWidget()
        screen_pink = gtk.EventBox()
        screen_pink.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
        screen_box = gtk.EventBox()
        screen_box.set_border_width(5)
        screen_box.add(self.screen)
        screen_pink.add(screen_box)
        screen_pink.props.border_width = 20

        # tape

        tape = gtk.HBox()

        for i in range(TAPE_COUNT):
            frame_box = gtk.VBox()

            filmstrip_pixbuf = gtk.gdk.pixbuf_new_from_file_at_scale(
                    Theme.path('icons/filmstrip.png'), THUMB_SIZE, -1, False)

            filmstrip = gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            frame_box.pack_start(filmstrip, False, False)

            frame = gtk.EventBox()
            frame.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            frame.connect('button_press_event', self._tape_cb, i)
            frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLACK))
            frame.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(BLACK))
            frame.props.border_width = 2
            frame.set_size_request(Theme.THUMB_SIZE, Theme.THUMB_SIZE)
            frame_box.pack_start(frame, False, False)
            self.tape.append(frame)

            frame_image = gtk.Image()
            frame_image.set_from_pixbuf(Theme.EMPTY_THUMB)
            frame.add(frame_image)

            filmstrip = gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            frame_box.pack_start(filmstrip, False, False)

            tape.pack_start(frame_box, False, False)

        self.tape_selected = -1

        # left control box
        
        self.controlbox = gtk.VBox()
        self.controlbox.props.border_width = 10
        self.controlbox.props.spacing = 10

        leftbox = gtk.VBox()
        logo = gtk.Image()
        logo.set_from_file(Theme.path('icons/logo.png'))
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
        tape_scroll = HScrolledBox(gtk.POLICY_ALWAYS)
        tape_scroll.set_viewport(tape)
        tape_scroll.modify_bg(gtk.STATE_NORMAL,
                gtk.gdk.color_parse(BUTTON_BACKGROUND))

        arrow = gtk.Image()
        arrow.set_from_file(Theme.path('icons/pink_arrow.png'))
        animborder = gtk.EventBox()
        animborder.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(PINK))
        animframe = gtk.EventBox()
        animframe.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BACKGROUND))
        animframe.set_border_width(5)
        animframe.add(tape_scroll)
        animborder.add(animframe)
        #animbox = gtk.HBox()
        #animbox.pack_start(animborder)

        tape_box = gtk.VBox()
        tape_box.props.border_width = 10
        tape_box.pack_start(arrow, False, False)
        tape_box.pack_start(animborder)

        desktop = gtk.VBox()
        desktop.pack_start(hdesktop,True,True,0)
        desktop.pack_start(tape_box, False, False, 0)

        greenbox = gtk.EventBox()
        greenbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        greenbox.set_border_width(5)
        greenbox.add(desktop)

        yellowbox = gtk.EventBox()
        yellowbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        yellowbox.add(greenbox)
        yellowbox.show_all()

        self.main = yellowbox
        yellowbox.connect_after('map', self.restore)

    def restore(self, widget):
        def new_combo(themes, cb, selname = None, closure = None):
            combo = ComboBox()
            sel = 0

            for i, theme in enumerate(themes):
                if theme:
                    combo.append_item(theme, text = theme.name,
                            size = (Theme.THUMB_SIZE, Theme.THUMB_SIZE),
                            pixbuf = theme.thumb())
                    if theme.name == selname:
                        sel = i
                else:
                    combo.append_separator()

            combo.connect('changed', cb, closure)
            combo.set_active(sel)
            combo.show()

            return combo

        self.controlbox.pack_start(new_combo(Char.THEMES, self._char_cb),
                True, False)
        self.controlbox.pack_start(new_combo(Ground.THEMES, self._combo_cb,
                Document.ground_name, self._ground_cb), True, False)
        self.controlbox.pack_start(new_combo(Sound.THEMES, self._combo_cb,
                Document.sound_name, self._sound_cb), True, False)

        for i in range(Theme.TAPE_COUNT):
            self.tape[i].child.set_from_pixbuf(Theme.scale(Document.tape[i].orig))
        self._tape_cb(None, None, 0)

        return False

    def play(self):
        self.play_tape_num = 0
        self._playing = gobject.timeout_add(self.waittime, self._play_tape)

    def stop(self):
        self._playing = None

    def set_tempo(self, tempo):
        self.waittime = int((6-tempo) * 150)
        if self._playing:
            gobject.source_remove(self._playing)
            self._playing = gobject.timeout_add(self.waittime, self._play_tape)

    def clear_tape(self):
        for i in range(TAPE_COUNT):
            Document.tape[i].clean()
        self.screen.fgpixbuf = Document.tape[self.tape_selected].orig
        self.screen.draw()

    def _play_tape(self):
        self.screen.fgpixbuf = Document.tape[self.play_tape_num].orig
        self.screen.draw()

        self.play_tape_num += 1
        if self.play_tape_num == TAPE_COUNT:
            self.play_tape_num = 0

        if self._playing:
            return True
        else:
            return False

    def _tape_cb(self, widget, event, index):
        tape = self.tape[index]
        tape.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(YELLOW))
        tape.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(YELLOW))

        if self.tape_selected != index:
            if self.tape_selected != -1:
                old_tape = self.tape[self.tape_selected]
                old_tape.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BLACK))
                old_tape.modify_bg(gtk.STATE_PRELIGHT,gtk.gdk.color_parse(BLACK))

        self.tape_selected = index
        self.screen.fgpixbuf = Document.tape[index].orig
        self.screen.draw()

    def _frame_cb(self, widget, event, frame):
        orig = self.char.orig(frame)
        if not orig: return
        thumb = self.char.thumb(frame)

        Document.tape[self.tape_selected].orig = orig
        Document.tape[self.tape_selected].filename = self.char.filename(frame)

        self.tape[self.tape_selected].child.set_from_pixbuf(thumb)
        self.frames[frame].set_from_pixbuf(thumb)
        self._tape_cb(None, None, self.tape_selected)

    def _char_cb(self, widget, closure):
        self.char = widget.props.value
        for i in range(len(self.frames)):
            self.frames[i].set_from_pixbuf(self.char.thumb(i))

    def _combo_cb(self, widget, cb):
        choice = widget.props.value.change()

        if not choice:
            widget.set_active(self._prev_combo_selected[widget])
            return

        if id(choice) != id(widget.props.value):
            pos = widget.get_active()
            widget.append_item(choice, text = choice.name,
                    size = (Theme.THUMB_SIZE, Theme.THUMB_SIZE),
                    pixbuf = choice.thumb(), position = pos)
            widget.set_active(pos)

        self._prev_combo_selected[widget] = widget.get_active()
        cb(choice)

    def _ground_cb(self, choice):
        self.screen.bgpixbuf = choice.orig()
        self.screen.draw()
        Document.ground_name = choice.name
        Document.ground_orig = choice.orig()
        Document.ground_filename = choice.filename()

    def _sound_cb(self, choice):
        Document.sound_name = choice.name
        Document.sound_filename = choice.filename()

    def _screen_size_cb(self, widget, aloc):
        size = min(aloc.width, aloc.height)
        widget.child.set_size_request(size, size)
