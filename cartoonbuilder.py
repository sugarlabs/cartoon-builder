#!/usr/bin/env python
#
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
import StringIO
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gettext
import os
import zipfile
import textwrap
import pickle
# should really put a try in front of this
# in case there is no sound support
import gst
from sugar.activity.activity import get_activity_root

from ComboBox import *
from Shared import *
import Char

_ = gettext.lgettext

TRANSIMG = '50x50blank-trans.png'
BGHEIGHT = gtk.gdk.screen_height() - 450 # 425
BGWIDTH = BGHEIGHT # 425
IMGHEIGHT = 100
IMGWIDTH = 100

BORDER_LEFT = 1
BORDER_RIGHT = 2
BORDER_TOP = 4
BORDER_BOTTOM = 8
BORDER_VERTICAL = BORDER_TOP | BORDER_BOTTOM
BORDER_HORIZONTAL = BORDER_LEFT | BORDER_RIGHT
BORDER_ALL = BORDER_VERTICAL | BORDER_HORIZONTAL
BORDER_ALL_BUT_BOTTOM = BORDER_HORIZONTAL | BORDER_TOP
BORDER_ALL_BUT_LEFT = BORDER_VERTICAL | BORDER_RIGHT

SLICE_BTN_WIDTH = 40

# Colors from the Rich's UI design

GRAY = "#B7B7B7" # gray
PINK = "#FF0099" # pink
YELLOW = "#FFFF00" # yellow
WHITE = "#FFFFFF"
BLACK = "#000000"
BACKGROUND = "#66CC00" # light green
BUTTON_FOREGROUND = "#CCFB99" # very light green
BUTTON_BACKGROUND = "#027F01" # dark green
COLOR_FG_BUTTONS = (
    (gtk.STATE_NORMAL,"#CCFF99"),
    (gtk.STATE_ACTIVE,"#CCFF99"),
    (gtk.STATE_PRELIGHT,"#CCFF99"),
    (gtk.STATE_SELECTED,"#CCFF99"),
    (gtk.STATE_INSENSITIVE,"#CCFF99"),
    ) # very light green
COLOR_BG_BUTTONS = (
    (gtk.STATE_NORMAL,"#027F01"),
    (gtk.STATE_ACTIVE,"#CCFF99"),
    (gtk.STATE_PRELIGHT,"#016D01"),
    (gtk.STATE_SELECTED,"#CCFF99"),
    (gtk.STATE_INSENSITIVE,"#027F01"),
    )
OLD_COLOR_BG_BUTTONS = (
    (gtk.STATE_NORMAL,"#027F01"),
    (gtk.STATE_ACTIVE,"#014D01"),
    (gtk.STATE_PRELIGHT,"#016D01"),
    (gtk.STATE_SELECTED,"#027F01"),
    (gtk.STATE_INSENSITIVE,"#027F01"),
    )

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

FRAME_COUNT = (gtk.gdk.screen_height() - 370) / IMGHEIGHT * 2
TAPE_COUNT = (gtk.gdk.screen_width() - 430) / IMGWIDTH

TMPDIR = os.path.join(get_activity_root(), 'tmp')

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

def prepare_btn(btn, w=-1, h=-1):
    for state, color in COLOR_BG_BUTTONS:
        btn.modify_bg(state, gtk.gdk.color_parse(color))
    c = btn.get_child()
    if c is not None:
        for state, color in COLOR_FG_BUTTONS:
            c.modify_fg(state, gtk.gdk.color_parse(color))
    else:
        for state, color in COLOR_FG_BUTTONS:
            btn.modify_fg(state, gtk.gdk.color_parse(color))
    if w>0 or h>0:
        btn.set_size_request(w, h)
    return btn

class FrameWidget(gtk.DrawingArea):
    def __init__(self,bgpixbuf,fgpixbuf):
        gtk.DrawingArea.__init__(self)
        self.gc = None  # initialized in realize-event handler
        self.width  = 0 # updated in size-allocate handler
        self.height = 0 # idem
        self.bgpixbuf = bgpixbuf
        self.fgpixbuf = fgpixbuf
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


class cartoonbuilder:
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def on_gstmessage(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            # END OF SOUND FILE
            self.player.set_state(gst.STATE_NULL)
            self.player.set_state(gst.STATE_PLAYING)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)

    def clearframe(self, widget, data=None):
        transpixbuf = self.gettranspixbuf(IMGWIDTH,IMGHEIGHT)
        self.frameimgs[self.frame_selected].set_from_pixbuf(transpixbuf)
        self.fgpixbufs[self.frame_selected] = self.gettranspixbuf(BGWIDTH,BGHEIGHT)
        self.fgpixbuf = self.gettranspixbuf(BGWIDTH,BGHEIGHT)
        self.drawmain()

    def clearall(self, widget, data=None):
        for i in range(TAPE_COUNT):
            transpixbuf = self.gettranspixbuf(IMGWIDTH,IMGHEIGHT)
            self.frameimgs[i].set_from_pixbuf(transpixbuf)
            self.fgpixbufs[i] = self.gettranspixbuf(BGWIDTH,BGHEIGHT)
        self.fgpixbuf = self.gettranspixbuf(BGWIDTH,BGHEIGHT)

    def selectframe(self, widget, event, data=None):
        if data:
            i = data-1
            self.framebuttons[i].modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
            self.framebuttons[i].modify_bg(gtk.STATE_PRELIGHT,gtk.gdk.color_parse(YELLOW))
            if self.frame_selected != i:
                self.framebuttons[self.frame_selected].modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BLACK))
                self.framebuttons[self.frame_selected].modify_bg(gtk.STATE_PRELIGHT,gtk.gdk.color_parse(BLACK))
                #self.framebuttons[self.frame_selected].set_style(self.fbstyle)
                self.frame_selected = i
                self.fgpixbuf = self.fgpixbufs[self.frame_selected]
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

    def lastback(self, widget, data=None):
        if self.backnum == 0:
            self.backnum = len(self.backpicpaths)-1
        else:
            self.backnum -= 1
        bgimgpath = self.backpicpaths[self.backnum]
        self.setback(bgimgpath)

    def nextback(self, widget, data=None):
        if self.backnum == (len(self.backpicpaths)-1):
            self.backnum = 0
        else:
            self.backnum += 1
        bgimgpath = self.backpicpaths[self.backnum]
        self.setback(bgimgpath)

    def setback(self,imgpath):
        #self.mfdraw.queue_draw()
        #pixbuf = gtk.gdk.pixbuf_new_from_file(self.bgimgpath)
        pixbuf = gtk.gdk.pixbuf_new_from_file(imgpath)
        self.bgpixbuf = pixbuf.scale_simple(BGWIDTH,BGHEIGHT,gtk.gdk.INTERP_BILINEAR)
        scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
        self.bgsmall.set_from_pixbuf(scaled_buf)
        self.drawmain()

    def _char_cb(self, widget):
        if self.imgdirindex == 0:
            self.imgdirindex = (len(self.imgdirs)-1)
        else:
            self.imgdirindex -= 1

        self.imgstartindex = 0
        self.imgdir = self.imgdirs[self.imgdirindex]
        self.loadimages()
        self.drawmain()

    def changesound(self):
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

    def lastsound(self, widget, data=None):
        if self.soundindex == 0:
            self.soundindex = (len(self.sounds)-1)
        else:
            self.soundindex -= 1
        self.soundfile = self.sounds[self.soundindex]
        self.changesound()

    def nextsound(self, widget, data=None):
        if self.soundindex == (len(self.sounds)-1):
            self.soundindex = 0
        else:
            self.soundindex += 1
        self.soundfile = self.sounds[self.soundindex]
        self.changesound()

    def go(self, widget, data=None):
        self.playframenum = 0
        if self.playing:
            if self.soundfile:
                self.player.set_state(gst.STATE_NULL)
            #widget.set_label('GO!')
            playimg = gtk.Image()
            #playimg.set_from_stock(gtk.STOCK_MEDIA_PLAY,gtk.ICON_SIZE_BUTTON)
            playimg.set_from_file(os.path.join(self.iconsdir,'big_right_arrow.png'))
            playimg.show()
            widget.set_image(playimg)
            self.playing = False
        else:
            if self.soundfile:
                #self.player.set_property('uri', 'file://' + self.soundfile)
                self.player.set_state(gst.STATE_PLAYING)
            #widget.set_label('STOP')
            stopimg = gtk.Image()
            #stopimg.set_from_stock(gtk.STOCK_MEDIA_STOP,gtk.ICON_SIZE_BUTTON)
            stopimg.set_from_file(os.path.join(self.iconsdir,'big_pause.png'))
            stopimg.show()
            widget.set_image(stopimg)
            self.playing = gobject.timeout_add(self.waittime, self.playframe)

    def oldplayframe(self):
        self.mfdraw.fgimgpath = self.frameimgpaths[self.playframenum]
        self.mfdraw.queue_draw()
        self.playframenum += 1
        if self.playframenum == TAPE_COUNT:
            self.playframenum = 0
        if self.playing:
            return True
        else:
            return False

    def playframe(self):
        self.fgpixbuf = self.fgpixbufs[self.playframenum]
        self.drawmain()
        self.playframenum += 1
        if self.playframenum == TAPE_COUNT:
            self.playframenum = 0
        # SOUND HANDLING
        #if self.bus.have_pending:
        #    print 'PENDING ITEMS ON SOUND BUS'
        # END OF SOUND HANDLING
        if self.playing:
            return True
        else:
            return False

    def drawmain(self):
        #if not self.fgimgpath:
        #    pixbuf2 = gtk.gdk.pixbuf_new_from_file(self.bgimgpath)
        #    sbuf2 = pixbuf2.scale_simple(BGHEIGHT,BGWIDTH,gtk.gdk.INTERP_BILINEAR)
        #    self.mainimage.set_from_pixbuf(sbuf2)
        #    return

        # COMPOSITING FROM FILE PATHS
        #pixbuf = gtk.gdk.pixbuf_new_from_file(self.fgimgpath)
        #sbuf = pixbuf.scale_simple(BGHEIGHT,BGWIDTH,gtk.gdk.INTERP_BILINEAR)
        #pixbuf2 = gtk.gdk.pixbuf_new_from_file(self.bgimgpath)
        #sbuf2 = pixbuf2.scale_simple(BGHEIGHT,BGWIDTH,gtk.gdk.INTERP_BILINEAR)
        #sbuf.composite(sbuf2,0,0,sbuf.props.width,sbuf.props.height,
        #                 0,0,1.0,1.0,gtk.gdk.INTERP_HYPER,255)

        # COMPOSITING FROM PIXBUFS
        #sbuf = self.fgpixbuf.copy()
        #sbuf2 = self.bgpixbuf.copy()
        #sbuf.composite(sbuf2,0,0,sbuf.props.width,sbuf.props.height,
        #                 0,0,1.0,1.0,gtk.gdk.INTERP_HYPER,255)
        #self.mainimage.set_from_pixbuf(sbuf2)

        # USING DRAWING AREA
        self.mfdraw.fgpixbuf = self.fgpixbuf
        self.mfdraw.bgpixbuf = self.bgpixbuf
        self.mfdraw.queue_draw()

    def setplayspeed(self,adj):
        self.waittime = int((6-adj.value)*150)
        if self.playing:
            gobject.source_remove(self.playing)
            self.playing = gobject.timeout_add(self.waittime, self.playframe)

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
        pics = self.getpics(self.imgdir)
        if self.imgstartindex > 0:
            self.imgstartindex -= 2
            self.loadimages()
            self.drawmain()

    def imgdown(self, widget, data=None):
        pics = self.getpics(self.imgdir)
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

    """
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

    def __init__(self,insugar,toplevel_window,mdirpath):
        self.mdirpath = mdirpath
        if not os.path.isdir(TMPDIR):
            os.mkdir(TMPDIR)
        self.iconsdir = os.path.join(self.mdirpath,'icons')
        self.playing = False
        self.backnum = 0
        self.backpicpaths = []
        bpfile = file(os.path.join(self.mdirpath,'config.backpics'))
        for line in bpfile:
            bpfilepath = line.strip()
            if bpfilepath[0] != '/':
                bpfilepath = os.path.join(self.mdirpath,line.strip())
            if os.path.isfile(bpfilepath):
                self.backpicpaths.append(bpfilepath)
        bpfile.close()
        self.waittime = 3*150
        self.imgdirs = []
        imgdirfile = file(os.path.join(self.mdirpath,'config.imgdirs'))
        for line in imgdirfile:
            imgdirpath = line.strip()
            if imgdirpath[0] != '/':
                imgdirpath = os.path.join(self.mdirpath,line.strip())
            if os.path.isdir(imgdirpath):
                self.imgdirs.append(imgdirpath)
        imgdirfile.close()
        self.imgdirindex = 0
        self.imgstartindex = 0
        self.sounds = ['']
        soundfile = file(os.path.join(self.mdirpath,'config.sounds'))
        for line in soundfile:
            soundfilepath = line.strip()
            if soundfilepath[0] != '/':
                soundfilepath = os.path.join(self.mdirpath,line.strip())
            if os.path.isfile(soundfilepath):
                self.sounds.append(soundfilepath)
        soundfile.close()
        self.soundindex = 0
        self.soundfile = self.sounds[self.soundindex]
        # START GSTREAMER STUFF
        self.player = gst.element_factory_make("playbin", "player")
        fakesink = gst.element_factory_make('fakesink', "my-fakesink")
        self.player.set_property("video-sink", fakesink)
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.on_gstmessage)
        # END GSTREAMER STUFF
        self.fgpixbuf = self.gettranspixbuf(BGWIDTH,BGHEIGHT)







        self.langoframe = gtk.EventBox()
        self.langoframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        self.langoframe.show()
        self.langframe = gtk.EventBox()
        self.langframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        self.langframe.show()
        self.langalign = gtk.Alignment(1.0,1.0,1.0,1.0)
        self.langalign.add(self.langframe)
        self.langalign.set_padding(5,0,5,5)
        self.langalign.show()
        self.langoframe.add(self.langalign)
        self.langhbox = gtk.HBox()
        self.langhbox.show()
        #self.langhbox.pack_start(self.llvbox,True,False,0)
        #self.langhbox.pack_start(self.langvbox,True,False,0)
        #self.langhbox.pack_start(self.nlvbox,True,False,0)
        self.langframe.add(self.langhbox)
        #self.logobox.pack_start(self.langoframe,True,True,0)



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
        prepare_btn(self.imgupbutton)
        self.iubhbox = gtk.HBox()
        self.iubhbox.show()
        self.iubhbox.pack_start(self.imgupbutton,True,False,0)
        self.tvbox.pack_start(self.iubhbox,False,False,5)

        for i in range(FRAME_COUNT/2):
            self.table.attach(self.imgbuttons[i*2], 0, 1, i, i+1)
            self.table.attach(self.imgbuttons[i*2+1], 1, 2, i, i+1)

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
        prepare_btn(self.imgdownbutton)
        self.idbhbox = gtk.HBox()
        self.idbhbox.show()
        self.idbhbox.pack_start(self.imgdownbutton,True,False,0)
        self.tvbox.pack_start(self.idbhbox,False,False,5)

        self.imgdir = self.imgdirs[self.imgdirindex]
        self.loadimages()

        # ANIMATION FRAMES / FILMSTRIP
        self.tophbox = gtk.HBox()
        self.tophbox.show()
        # animation frames        
        self.animhbox = gtk.HBox()
        self.animhbox.show()
        self.framebuttons = []
        self.frameimgs = []
        self.fgpixbufs = []
        self.fgpixbufpaths = []
        transimgpath = os.path.join(self.iconsdir,TRANSIMG)
        for i in range(TAPE_COUNT):
            #fb = gtk.Button()
            #fb.connect('clicked', self.selectframe, i+1)
            fb = gtk.EventBox()
            fb.set_events(gtk.gdk.BUTTON_PRESS_MASK)
            fb.connect('button_press_event', self.selectframe, i+1)
            fb.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BLACK))
            fb.modify_bg(gtk.STATE_PRELIGHT,gtk.gdk.color_parse(BLACK))
            fb.show()
            self.framebuttons.append(fb)
            tpixbuf = self.gettranspixbuf(BGWIDTH,BGHEIGHT)
            self.fgpixbufs.append(tpixbuf)
            self.fgpixbufpaths.append(transimgpath)
            #fb.set_label('')
            transimg = gtk.Image()
            transimg.set_from_pixbuf(self.gettranspixbuf(IMGWIDTH,IMGHEIGHT))
            transimg.show()
            self.frameimgs.append(transimg)
            #fb.set_image(transimg)
            fb.add(transimg)
            self.animhbox.pack_start(fb,True,True,2)
            #if i != 5:
            #    ra = gtk.Arrow(gtk.ARROW_RIGHT,gtk.SHADOW_OUT)
            #    ra.show()
            #    self.tophbox.pack_start(ra,True,True,0)


        self.animborder = gtk.EventBox()
        self.animborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
        self.animborder.show()
        self.animframe = gtk.EventBox()
        self.animframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        self.animframe.set_border_width(5)
        self.animframe.show()
        self.animborder.add(self.animframe)
        self.animfilmstrip = gtk.VBox()
        self.animfilmstrip.show()

        filmstrip_pix = gtk.gdk.pixbuf_new_from_file(os.path.join(
                self.iconsdir,'filmstrip.png'))
        filmstrip_pix = filmstrip_pix.scale_simple(
                (IMGWIDTH + 4) * TAPE_COUNT, filmstrip_pix.get_height(),
                gtk.gdk.INTERP_BILINEAR)

        self.filmstriptopimg = gtk.Image()
        self.filmstriptopimg.set_from_pixbuf(filmstrip_pix)
        self.filmstriptopimg.show()
        self.animfilmstrip.pack_start(self.filmstriptopimg,True,True,0)
        self.animfilmstrip.pack_start(self.animhbox,False,False,0)
        self.filmstripbottomimg = gtk.Image()
        self.filmstripbottomimg.set_from_pixbuf(filmstrip_pix)
        self.filmstripbottomimg.show()
        self.animfilmstrip.pack_start(self.filmstripbottomimg,False,False,0)
        self.animframe.add(self.animfilmstrip)
        self.afvbox = gtk.VBox()
        self.afvbox.show()
        self.afvbox.pack_start(self.animborder,False,False,0)
        self.tophbox.pack_start(self.afvbox,False,False,0)
        #self.clrframe = gtk.Button('CLEAR FRAME')
        cancelimg = gtk.Image()
        #cancelimg.set_from_stock(gtk.STOCK_CANCEL,gtk.ICON_SIZE_BUTTON)
        cancelimg.set_from_file(os.path.join(self.iconsdir,'clear.png'))
        cancelimg.show()
        self.clrframe = gtk.Button()
        self.clrframe.set_label('')
        self.clrframe.set_image(cancelimg)
        self.clrframe.connect('clicked', self.clearall, None)
        prepare_btn(self.clrframe)
        self.clrframe.show()
        
        #self.cfbox.pack_start(self.clrframe,True,True,0)
        #self.clrall = gtk.Button('CLEAR ALL')
        #self.clrall.connect('clicked', self.clearall, None)
        #self.clrall.show()
        #self.cfbox.pack_start(self.clrall,True,True,0)
        #self.controlbox.pack_start(self.cfbox,True,True,0)
        self.cfvbox = gtk.VBox()
        self.cfvbox.show()
        self.cfvbox.pack_start(self.clrframe,True,False,0)
        self.tophbox.pack_start(self.cfvbox,False,False,5)

        self.frame_selected = 0
        self.fbstyle = self.framebuttons[0].get_style()
        self.framebuttons[0].modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
        self.framebuttons[0].modify_bg(gtk.STATE_PRELIGHT,gtk.gdk.color_parse(YELLOW))

        self.centervbox = gtk.VBox()
        self.centervbox.show()
        # MAIN IMAGE
        self.mfdraw = FrameWidget(None,self.fgpixbuf)
        self.mfdraw.set_size_request(BGWIDTH,BGHEIGHT)
        self.mfdraw.show()
        self.mfdrawborder = gtk.EventBox()
        self.mfdrawborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(PINK))
        self.mfdrawborder.show()
        self.mfdrawbox = gtk.EventBox()
        self.mfdrawbox.set_border_width(5)
        self.mfdrawbox.show()
        self.mfdrawbox.add(self.mfdraw)
        self.mfdrawborder.add(self.mfdrawbox)
        self.centervbox.pack_end(self.mfdrawborder,True,False,0)

        self.bcontrolbox = gtk.HBox()
        self.bcontrolbox.set_border_width(5)
        self.bcontrolbox.show()
        # GO BUTTON
        playimg = gtk.Image()
        #playimg.set_from_stock(gtk.STOCK_MEDIA_PLAY,gtk.ICON_SIZE_BUTTON)
        playimg.set_from_file(os.path.join(self.iconsdir,'big_right_arrow.png'))
        playimg.show()
        self.gobutton = gtk.Button()
        self.gobutton.set_label('')
        self.gobutton.set_image(playimg)
        self.gobutton.connect('clicked', self.go, None)
        prepare_btn(self.gobutton)
        self.gobutton.show()
        self.bcontrolbox.pack_start(self.gobutton,True,True,5)
        
        # SPEED CONTROLS
        self.sbox = gtk.VBox()
        self.sbox.show()
        adj = gtk.Adjustment(2.5,1,5,.5,1)
        adj.connect('value_changed',self.setplayspeed)
        self.playspeed = gtk.HScale(adj)
        self.playspeed.set_draw_value(False)
        for state, color in COLOR_BG_BUTTONS:
            self.playspeed.modify_bg(state, gtk.gdk.color_parse(color))
        self.playspeed.show()
        self.sbox.pack_start(self.playspeed,True,True,0)
        #self.pslabel = gtk.Label('Speed')
        #self.pslabel.show()
        #self.sbox.pack_start(self.pslabel,True,True,0)
        self.bcontrolbox.pack_start(self.sbox,True,True,5)
        self.centervbox.pack_start(self.bcontrolbox,False,False,0)        
        
        self.controlbox = gtk.VBox()
        self.controlbox.show()
        

        # CHARACTER CONTROLS
        char_box = BigComboBox()
        char_box.show()
        for i in Char.list():
            char_box.append_item(i.id, size = Char.Size,
                    pixbuf = i.pixbuf)
        char_box.connect('changed', self._char_cb)
        self.controlbox.pack_start(char_box, False, False, 5)

        # BACKGROUND CONTROLS


        self.bgbox = gtk.VBox()
        self.bgbox.show()
        self.bghbox = gtk.HBox()
        self.bghbox.show()
        self.blbutton = gtk.Button()
        self.blbutton.connect('clicked',self.lastback,None)
        self.blbutton.show()
        bla = gtk.Image()
        bla.set_from_file(os.path.join(self.iconsdir,'big_left_arrow.png'))
        bla.show()
        self.blbutton.add(bla)
        prepare_btn(self.blbutton)
        self.blbvbox = gtk.VBox()
        self.blbvbox.show()
        self.blbvbox.pack_start(self.blbutton,True,False,0)
        self.bghbox.pack_start(self.blbvbox,True,True,5)
        self.bgsmall = gtk.Image()
        bgimgpath = os.path.join(self.mdirpath,'backpics/bigbg01.gif')
        self.setback(bgimgpath)
        self.bgsmall.show()
        self.bghbox.pack_start(self.bgsmall,False,False,0)
        self.brbutton = gtk.Button()
        self.brbutton.connect('clicked',self.nextback,None)
        self.brbutton.show()
        bra = gtk.Image()
        bra.set_from_file(os.path.join(self.iconsdir,'big_right_arrow.png'))
        bra.show()
        self.brbutton.add(bra)
        prepare_btn(self.brbutton)
        self.brbvbox = gtk.VBox()
        self.brbvbox.show()
        self.brbvbox.pack_start(self.brbutton,True,False,0)
        self.bghbox.pack_start(self.brbvbox,True,True,5)
        self.bgbox.pack_start(self.bghbox,True,True,0)
        self.controlbox.pack_start(self.bgbox,False,False,5)
        
        # SOUND CONTROLS
        self.soundbox = gtk.VBox()
        self.soundbox.show()
        self.soundhbox = gtk.HBox()
        self.soundhbox.show()
        self.slbutton = gtk.Button()
        self.slbutton.connect('clicked',self.lastsound,None)
        self.slbutton.show()
        sla = gtk.Image()
        sla.set_from_file(os.path.join(self.iconsdir,'big_left_arrow.png'))
        sla.show()
        self.slbutton.add(sla)
        prepare_btn(self.slbutton)
        self.slbvbox = gtk.VBox()
        self.slbvbox.show()
        self.slbvbox.pack_start(self.slbutton,True,False,0)
        self.soundhbox.pack_start(self.slbvbox,True,True,5)
        self.soundimg = gtk.Image()
        #self.soundimg.set_from_file(os.path.join(self.iconsdir,'sound_icon.png'))
        soundimgpath = os.path.join(self.iconsdir,'sound_icon.png')
        sipixbuf = gtk.gdk.pixbuf_new_from_file(soundimgpath)
        si_scaled_buf = sipixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
        self.soundimg.set_from_pixbuf(si_scaled_buf)
        self.soundimg.show()
        self.soundhbox.pack_start(self.soundimg,False,False,0)
        self.srbutton = gtk.Button()
        self.srbutton.connect('clicked',self.nextsound,None)
        self.srbutton.show()
        sra = gtk.Image()
        sra.set_from_file(os.path.join(self.iconsdir,'big_right_arrow.png'))
        sra.show()
        self.srbutton.add(sra)
        prepare_btn(self.srbutton)
        self.srbvbox = gtk.VBox()
        self.srbvbox.show()
        self.srbvbox.pack_start(self.srbutton,True,False,0)
        self.soundhbox.pack_start(self.srbvbox,True,True,5)
        self.soundbox.pack_start(self.soundhbox,True,True,0)
        self.soundlabel = gtk.Label('No Sound')
        self.soundlabel.show()
        self.soundlabelhbox = gtk.HBox()
        self.soundlabelhbox.show()
        self.soundlabelhbox.pack_start(self.soundlabel,True,False,0)
        self.soundbox.pack_start(self.soundlabelhbox,False,False,0)
        self.controlbox.pack_start(self.soundbox,False,False,5)
        





        self.centerframe = gtk.EventBox()
        self.centerframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
        self.centerframe.set_border_width(5)
        self.centerframe.show()
        #self.ocenterframe.add(self.centerframe)






        leftbox = gtk.VBox()
        leftbox.show()

        self.logo = gtk.Image()
        self.logo.show()
        self.logo.set_from_file(os.path.join(self.iconsdir,'logo.png'))
        leftbox.pack_start(self.logo,False,False,0)

        self.bottomhbox = gtk.HBox()
        self.bottomhbox.show()
        leftbox.pack_start(self.bottomhbox,True,True,10)
        self.bottomhbox.pack_start(self.controlbox,False,False,10)




        cetralbox = gtk.HBox()
        cetralbox.show()
        cetralbox.pack_start(self.centervbox,True,False,0)
        cetralbox.pack_start(self.tvbox,False,True,0)




        hdesktop = gtk.HBox()
        hdesktop.show()
        hdesktop.pack_start(leftbox,False,True,0)
        hdesktop.pack_start(cetralbox,True,True,0)

        pink_arrow = gtk.Image()
        pink_arrow.set_from_file(os.path.join(self.iconsdir, 'pink_arrow.png'))
        pink_arrow.show()
        self.pahbox = gtk.HBox()
        self.pahbox.show()
        self.pahbox.pack_start(pink_arrow,False,False,150)

        self.topvbox = gtk.VBox()
        self.topvbox.show()
        self.topvbox.pack_start(self.tophbox,False,False,0)
        self.topvbox.pack_start(self.pahbox,False,False,0)

        desktop = gtk.VBox()
        desktop.show()
        #desktop.pack_start(self.logobox,False,False,0)
        desktop.pack_start(hdesktop,True,True,0)
        desktop.pack_end(self.topvbox, False, False, 0)

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

try:
    from sugar.graphics.toolbutton import ToolButton
    from sugar.graphics.objectchooser import ObjectChooser
    
    class BGToolbar(gtk.Toolbar):
        def __init__(self,sactivity,app):
            gtk.Toolbar.__init__(self)
            self.sactivity = sactivity
            self.app = app
            self.image = ToolButton('insert-image')
            self.image.set_tooltip('Insert Image')
            self.imageid = self.image.connect('clicked',self.image_cb)
            self.insert(self.image,-1)
            self.image.show()

        def image_cb(self, button):
            chooser = ObjectChooser('Choose Image',self.sactivity,
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

    class cartoonbuilderActivity(Shared):
        def __init__(self, handle):
            Shared.__init__(self,handle)
            self.connect("destroy",self.destroy_cb)
            #app = cartoonbuilder(self,'/home/olpc/Activities/CartoonBuilder.activity')
            bundle_path = activity.get_bundle_path()
            os.chdir(bundle_path)
            self.app = cartoonbuilder(True,self, bundle_path)
            self.set_title('CartoonBuilder')
            toolbox = activity.ActivityToolbox(self)
            bgtoolbar = BGToolbar(self,self.app)
            toolbox.add_toolbar(_('Background'),bgtoolbar)
            bgtoolbar.show()
            self.set_toolbox(toolbox)
            toolbox.show()
            if hasattr(self, '_jobject'):
                self._jobject.metadata['title'] = 'CartoonBuilder'
            title_widget = toolbox._activity_toolbar.title
            title_widget.set_size_request(title_widget.get_layout().get_pixel_size()[0] + 20, -1)
            self.set_canvas(self.app.main)

        def destroy_cb(self, data=None):
            return True

        def read_file(self, filepath):
            Bundle.load(filepath)

        def write_file(self, filepath):
            Bundle.save(filepath)


except ImportError:
    pass

if __name__ == "__main__":
    # have to do toplevel window stuff here because Sugar does it on the OLPC
    toplevel_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    #mdirpath = '.'
    mdirpath = os.path.abspath(os.curdir)
    app = cartoonbuilder(False,toplevel_window,mdirpath)
    toplevel_window.add(app.main)
    toplevel_window.set_title('Cartoon Builder')
    # FULLSCREEN

    #toplevel_window.set_decorated(False)
    #toplevel_window.fullscreen()
    
    toplevel_window.connect("delete_event", app.delete_event)
    toplevel_window.connect("destroy", app.destroy)
    #toplevel_window.set_border_width(10)
    toplevel_window.show()
    gtk.main()
