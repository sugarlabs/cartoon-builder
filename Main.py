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
import Document
from Utils import *
from Shared import *

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
        self.width = allocation.width
        self.height = allocation.height
    
    def on_expose_event(self, widget, event):
        # This is where the drawing takes place
        if self.bgpixbuf:
            #bgpixbuf = gtk.gdk.pixbuf_new_from_file(self.bgimgpath)
            widget.window.draw_pixbuf(self.gc,self.bgpixbuf,0,0,0,0,-1,-1,0,0)
        if self.fgpixbuf:
            #fgpixbuf = gtk.gdk.pixbuf_new_from_file(self.fgimgpath)
            #widget.window.draw_pixbuf(self.gc,fgpixbuf,0,0,75,75,-1,-1,0,0)
            widget.window.draw_pixbuf(self.gc,self.fgpixbuf,0,0,0,0,-1,-1,0,0)

    def draw(self):
        self.queue_draw()

class CartoonBuilder:

    def play(self):
        self.play_tape_num = 0
        self._playing = gobject.timeout_add(self.waittime, self._play_tape)

    def stop():
        self._playing = None

    def set_tempo(self, tempo):
        self.waittime = int((6-tempo) * 150)
        if self._playing:
            gobject.source_remove(self._playing)
            self._playing = gobject.timeout_add(self.waittime, self._play_tape)

    def clear_tape(self):
        for i in range(TAPE_COUNT):
            Document.clean_pixbuf(i)
        self.screen.fgpixbuf = Document.get_pixbuf(self.tape_selected)
        self.screen.draw()


    def _play_tape(self):
        self.screen.fgpixbuf = Document.get_pixbuf(self.play_tape_num)
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
            self.screen.fgpixbuf = Document.get_pixbuf(index)
            self.screen.draw()

    def _ground_cb(self, widget, combo):
        choice = Ground.change(widget.props.value)

        if not choice:
            widget.set_active(self._prev_ground)
            return

        if id(choice) != id(widget.props.value):
            pos = combo.get_active()
            combo.append_item(choice, text = choice['name'],
                    size = (Theme.FRAME_SIZE, Theme.FRAME_SIZE),
                    pixbuf = choice['pixbuf'], position = pos)
            combo.set_active(pos)

        self._prev_ground = widget.get_active()
        self.screen.bgpixbuf = choice['pixbuf'].scale_simple(Theme.SCREEN_SIZE,
                Theme.SCREEN_SIZE, gtk.gdk.INTERP_BILINEAR)
        self.screen.draw()

    def _sound_cb(self, widget, combo):
        Sound.change(widget.props.value)

    def _char_cb(self, widget):
        return

        if self.imgdirindex == 0:
            self.imgdirindex = (len(self.imgdirs)-1)
        else:
            self.imgdirindex -= 1

        self.imgstartindex = 0
        self.imgdir = self.imgdirs[self.imgdirindex]
        self.loadimages()
        self.drawmain()















    def pickimage(self, widget, event, data=None):
        if data:
            pixbuf = self.posepixbufs[data-1]
            scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
            self.frameimgs[self.frame_selected].set_from_pixbuf(scaled_buf)
            fgpixbuf = pixbuf.scale_simple(BGWIDTH,BGHEIGHT,gtk.gdk.INTERP_BILINEAR)
            self.fgpixbufs[self.frame_selected] = fgpixbuf
            self.fgpixbufpaths[self.frame_selected] = self.poseimgpaths[data-1]
            self.fgpixbuf = fgpixbuf
            self.drawmain()




    def loadimages(self):
        self.posepixbufs = []
        self.poseimgpaths = []

        pics = self.getpics(self.imgdir)
        count = 0

        for imgpath in pics[self.imgstartindex:self.imgstartindex+FRAME_COUNT]:
            pixbuf = gtk.gdk.pixbuf_new_from_file(imgpath)
            scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
            self.posepixbufs.append(pixbuf)
            self.poseimgpaths.append(imgpath)
            self.images[count].set_from_pixbuf(scaled_buf)
            count += 1

        for i in range(count,FRAME_COUNT):
            transpixbuf = self.gettranspixbuf(IMGWIDTH,IMGHEIGHT)
            imgpath = os.path.join(self.iconsdir,TRANSIMG)
            img = gtk.Image()
            img.set_from_pixbuf(transpixbuf)
            img.show()
            self.posepixbufs.append(pixbuf)
            self.poseimgpaths.append(imgpath)
            self.images[i].set_from_pixbuf(transpixbuf)

    def getpics(self, dirpath):
        pics = []
        entries = os.listdir(dirpath)
        entries.sort()
        for entry in entries:
            if entry[-4:].lower() in ['.png','.gif','.jpg']:
                filepath = os.path.join(dirpath,entry)
                pics.append(filepath)
        return pics


    def imgup(self, widget, data=None):
        #pics = self.getpics(self.imgdir)
        if self.imgstartindex > 0:
            self.imgstartindex -= 2
            self.loadimages()
            self.drawmain()

    def imgdown(self, widget, data=None):
        #pics = self.getpics(self.imgdir)
        if len(pics[self.imgstartindex:]) > FRAME_COUNT:
            self.imgstartindex += 2
            self.loadimages()
            self.drawmain()

    def gettranspixbuf(self, width=50, height=50):
        transimgpath = os.path.join(self.iconsdir,TRANSIMG)
        pixbuf = gtk.gdk.pixbuf_new_from_file(transimgpath)
        if width == 50 and height == 50:
            return pixbuf
        scaled_buf = pixbuf.scale_simple(width,height,gtk.gdk.INTERP_BILINEAR)
        return scaled_buf





    def __init__(self,insugar,toplevel_window,mdirpath):
        self.mdirpath = mdirpath
        self.iconsdir = os.path.join(self.mdirpath, 'icons')
        self._playing = None

        self.waittime = 3*150


        self.imgstartindex = 0

        #self.loadimages()


        self.tvbox = gtk.VBox()
        self.tvbox.show()
        # flow arrows
        flowbox = gtk.HBox()
        flowbox.show()
        yellow_arrow = gtk.Image()
        yellow_arrow.set_from_file(os.path.join(self.iconsdir, 'yellow_arrow.png'))
        yellow_arrow.show()
        flowbox.pack_end(yellow_arrow,True,False,0)
        topspace = gtk.EventBox()
        topspace.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        topspace.show()
        topspace.set_border_width(15)
        self.tvbox.pack_start(topspace,False,False,0)
        self.tvbox.pack_start(flowbox,False,False,0)
        self.table = gtk.Table(rows=FRAME_COUNT/2, columns=2, homogeneous=False)

        self.imgbuttons = []
        self.images = []
        # POSE CHOOSER BUTTONS
        for i in range(1,11):
            ib = gtk.EventBox()
            #ib = gtk.Button()
            #ib.connect('clicked', self.pickimage, i)
            ib.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            ib.connect('button_press_event', self.pickimage, i)
            ib.set_border_width(1)
            #ib.add(img)
            ib.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BLACK))
            ib.modify_bg(gtk.STATE_PRELIGHT,gtk.gdk.color_parse(BLACK))
            ib.show()
            img = gtk.Image()
            img.show()
            #ib.set_label('')
            #ib.set_image(img)
            ib.add(img)
            self.imgbuttons.append(ib)
            self.images.append(img)

        self.imgupbutton = gtk.Button()
        self.imgupbutton.connect('clicked', self.imgup, None)
        self.imgupbutton.show()
        #upa = gtk.Arrow(gtk.ARROW_UP,gtk.SHADOW_OUT)
        #upa.show()
        upa = gtk.Image()
        upa.set_from_file(os.path.join(self.iconsdir,'big_up_arrow.png'))
        #upapixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(self.iconsdir,'up_arrow.png'))
        #scaled_upapixbuf = upapixbuf.scale_simple(42,34,gtk.gdk.INTERP_BILINEAR)
        #upa.set_from_pixbuf(scaled_upapixbuf)
        upa.show()

        self.imgupbutton.add(upa)
        self.iubhbox = gtk.HBox()
        self.iubhbox.show()
        self.iubhbox.pack_start(self.imgupbutton,True,False,0)
        self.tvbox.pack_start(self.iubhbox,False,False,5)

        #for i in range(FRAME_COUNT/2):
        #    self.table.attach(self.imgbuttons[i*2], 0, 1, i, i+1)
        #    self.table.attach(self.imgbuttons[i*2+1], 1, 2, i, i+1)

        self.table.show()

        self.tableframeborder = gtk.EventBox()
        self.tableframeborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        self.tableframeborder.show()
        self.tableframe = gtk.EventBox()
        self.tableframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        self.tableframe.show()
        self.tableframe.set_border_width(5)
        self.tableframeborder.add(self.tableframe)
        self.tableframe.add(self.table)

        self.tfhbox = gtk.HBox()
        self.tfhbox.show()
        self.tfhbox.pack_start(self.tableframeborder,True,False,20)
        self.tvbox.pack_start(self.tfhbox,False,False,0)
        
        self.imgdownbutton = gtk.Button()
        self.imgdownbutton.connect('clicked', self.imgdown, None)
        self.imgdownbutton.show()
        #downa = gtk.Arrow(gtk.ARROW_DOWN,gtk.SHADOW_OUT)
        #downa.show()
        downa = gtk.Image()
        downa.set_from_file(os.path.join(self.iconsdir,'big_down_arrow.png'))
        downa.show()
        self.imgdownbutton.add(downa)
        self.idbhbox = gtk.HBox()
        self.idbhbox.show()
        self.idbhbox.pack_start(self.imgdownbutton,True,False,0)
        self.tvbox.pack_start(self.idbhbox,False,False,5)




        self.framebuttons = []
        self.frameimgs = []
        self.fgpixbufs = []
        self.fgpixbufpaths = []
        self.tape = []



        # screen

        self.screen = FrameWidget()
        #self.screen.set_size_request(Theme.SCREEN_SIZE, Theme.SCREEN_SIZE)
        self.screen.show()
        screen_pink = gtk.EventBox()
        screen_pink.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
        screen_pink.show()
        screen_box = gtk.EventBox()
        screen_box.set_border_width(5)
        screen_box.show()
        screen_box.add(self.screen)
        screen_pink.add(screen_box)
        screen_pink.props.border_width = 20

        # tape

        tape = gtk.HBox()
        tape.show()

        for i in range(TAPE_COUNT):
            frame_box = gtk.VBox()
            frame_box.show()

            filmstrip_pixbuf = gtk.gdk.pixbuf_new_from_file_at_scale(
                    Theme.path('icons/filmstrip.png'), FRAME_SIZE, -1, False)

            filmstrip = gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            filmstrip.show()
            frame_box.pack_start(filmstrip, True, False)

            frame = gtk.EventBox()
            frame.show()
            frame.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            frame.connect('button_press_event', self._tape_cb, i)
            frame.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BLACK))
            frame.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse(BLACK))
            frame.props.border_width = 2
            frame.set_size_request(Theme.FRAME_SIZE, Theme.FRAME_SIZE)
            frame_box.pack_start(frame, False, False)
            self.tape.append(frame)

            frame_image = gtk.Image()
            frame_image.set_from_pixbuf(Document.get_pixbuf(i))
            frame_image.show()
            frame.add(frame_image)

            filmstrip = gtk.Image()
            filmstrip.set_from_pixbuf(filmstrip_pixbuf);
            filmstrip.show()
            frame_box.pack_start(filmstrip, False, False)

            tape.pack_start(frame_box, False, False)

        self.tape_selected = -1
        self._tape_cb(None, None, 0)

        # left control box
        
        def new_combo(themes, cb):
            combo = ComboBox()
            combo.show()
            for i in themes:
                if not i:
                    combo.append_separator()
                else:
                    combo.append_item(i, text = i['name'],
                            size = (Theme.FRAME_SIZE, Theme.FRAME_SIZE),
                            pixbuf = i['pixbuf'])
            combo.connect('changed', cb, combo)
            combo.set_active(0)
            return combo

        controlbox = gtk.VBox()
        controlbox.show()
        controlbox.props.border_width = 10
        controlbox.props.spacing = 10
        controlbox.pack_start(new_combo(Char.THEMES, self._char_cb),
                True, False)
        controlbox.pack_start(new_combo(Ground.THEMES, self._ground_cb),
                True, False)
        controlbox.pack_start(new_combo(Sound.THEMES, self._sound_cb),
                True, False)

        leftbox = gtk.VBox()
        leftbox.show()
        logo = gtk.Image()
        logo.show()
        logo.set_from_file(Theme.path('icons/logo.png'))
        leftbox.pack_start(logo, False, False)
        leftbox.pack_start(controlbox, True, True)
        
        # screen box

        cetralbox = gtk.HBox()
        cetralbox.show()
        cetralbox.pack_start(screen_pink, True, True)
        cetralbox.pack_start(self.tvbox, False, False)

        hdesktop = gtk.HBox()
        hdesktop.show()
        hdesktop.pack_start(leftbox,False,True,0)
        hdesktop.pack_start(cetralbox,True,True,0)

        # tape box

        arrow = gtk.Image()
        arrow.set_from_file(Theme.path('icons/pink_arrow.png'))
        arrow.show()
        animborder = gtk.EventBox()
        animborder.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(PINK))
        animborder.show()
        animframe = gtk.EventBox()
        animframe.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(BACKGROUND))
        animframe.set_border_width(5)
        animframe.show()
        animframe.add(tape)
        animborder.add(animframe)
        animbox = gtk.HBox()
        animbox.show()
        animbox.pack_start(animborder, True, False)
        tape_box = gtk.VBox()
        tape_box.props.border_width = 10
        tape_box.pack_start(arrow, False, False)
        tape_box.pack_start(animbox, False, False, 0)

        desktop = gtk.VBox()
        desktop.show()
        desktop.pack_start(hdesktop,True,True,0)
        desktop.pack_start(tape_box, False, False, 0)

        greenbox = gtk.EventBox()
        greenbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        greenbox.set_border_width(5)
        greenbox.show()
        greenbox.add(desktop)

        yellowbox = gtk.EventBox()
        yellowbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        yellowbox.show()
        yellowbox.add(greenbox)

        self.main = yellowbox
        self.main.show_all()

    def main(self):
        gtk.main()


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

