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

_ = gettext.lgettext

SERVICE = 'org.freedesktop.Telepathy.Tube.Connect'
IFACE = SERVICE
PATH = '/org/freedesktop/Telepathy/Tube/Connect'

TRANSIMG = '50x50blank-trans.png'
BGHEIGHT = 425
BGWIDTH = 425
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
        for i in range(6):
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

    def setcharacter(self):
	pics = self.getpics(self.imgdir)
	pixbuf = gtk.gdk.pixbuf_new_from_file(pics[self.imgstartindex])
	scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
	self.ccismall.set_from_pixbuf(scaled_buf)
        self.charlabel.set_label(os.path.split(self.imgdir)[1])

    def lastcharacter(self, widget, data=None):
        if self.imgdirindex == 0:
	    self.imgdirindex = (len(self.imgdirs)-1)
	else:
	    self.imgdirindex -= 1
	self.imgstartindex = 0
	self.imgdir = self.imgdirs[self.imgdirindex]
	self.loadimages()
	self.setcharacter()
	self.drawmain()

    def nextcharacter(self, widget, data=None):
        if self.imgdirindex == (len(self.imgdirs)-1):
	    self.imgdirindex = 0
	else:
	    self.imgdirindex += 1
	self.imgstartindex = 0
	self.imgdir = self.imgdirs[self.imgdirindex]
	self.loadimages()
	self.setcharacter()
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
	if self.playframenum == 6:
	    self.playframenum = 0
	if self.playing:
	    return True
	else:
	    return False

    def playframe(self):
	self.fgpixbuf = self.fgpixbufs[self.playframenum]
	self.drawmain()
	self.playframenum += 1
	if self.playframenum == 6:
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

    def getbackgroundfile(self, widget, data=None):
        dialog = gtk.FileChooserDialog(title="Open..",
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL, 
				       gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	if self.insugar:
	    dialog.set_current_folder('/home/olpc')
        dialog.set_default_response(gtk.RESPONSE_OK)

        #filter = gtk.FileFilter()
        #filter.set_name("All files")
        #filter.add_pattern("*")
        #dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.gif")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            #print dialog.get_filename(), 'selected'
	    bgimgpath = dialog.get_filename()
	    self.backpicpaths.append(bgimgpath)
	    self.backnum = self.backpicpaths.index(bgimgpath)
	    self.setback(bgimgpath)
	    f = file(os.path.join(self.mdirpath,'config.backpics'),'a')
	    f.write('%s\n' % bgimgpath)
	    f.close()
        elif response == gtk.RESPONSE_CANCEL:
            # print 'Closed, no files selected'
	    pass
        dialog.destroy()

    def getimgdir(self, widget, data=None):
        daction = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
        dialog = gtk.FileChooserDialog(title='Select Folder',
                                       action=daction,
                                       buttons=(gtk.STOCK_CANCEL, 
				       gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, 
				       gtk.RESPONSE_OK))
	if self.insugar:
	    dialog.set_current_folder('/home/olpc')
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            #print dialog.get_filename(), 'selected'
	    imgdir = dialog.get_filename()
	    pics = self.getpics(imgdir)
	    if pics:
	        self.imgdir = imgdir
		self.imgdirs.append(imgdir)
		self.imgdirindex = self.imgdirs.index(imgdir)
	        self.loadimages()
	        self.setcharacter()
	        self.drawmain()
	        f = file(os.path.join(self.mdirpath,'config.imgdirs'),'a')
	        f.write('%s\n' % imgdir)
	        f.close()
        elif response == gtk.RESPONSE_CANCEL:
	    pass
        dialog.destroy()

    def getsoundfile(self, widget, data=None):
        dialog = gtk.FileChooserDialog(title="Open..",
                                       action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                       buttons=(gtk.STOCK_CANCEL, 
				       gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	if self.insugar:
	    dialog.set_current_folder('/home/olpc')
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name("Sounds")
        #filter.add_mime_type("image/png")
        filter.add_pattern('*.wav')
	filter.add_pattern('*.mp3')
	filter.add_pattern('*.ogg')
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
	    soundfilepath = dialog.get_filename()
	    self.sounds.append(soundfilepath)
	    self.soundfile = soundfilepath
	    self.soundindex = self.sounds.index(soundfilepath)
	    self.changesound()
	    f = file(os.path.join(self.mdirpath,'config.sounds'),'a')
	    f.write('%s\n' % soundfilepath)
	    f.close()
        elif response == gtk.RESPONSE_CANCEL:
            # print 'Closed, no files selected'
	    pass
        dialog.destroy()

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
	tmpimgdir = os.path.join(self.mdirpath,'tmpimg')
	tmpbgpath = os.path.join(tmpimgdir,'back.png')
	self.bgpixbuf.save(tmpbgpath,'png')
	sdd['pngdata'] = file(tmpbgpath).read()
	os.remove(tmpbgpath)
	sdd['fgpixbufpaths'] = self.fgpixbufpaths
	#sdd['fgpixbufs'] = []
	#count = 1
	#for pixbuf in self.fgpixbufs:
	#    filename = '%02d.png' % count
	#    filepath = os.path.join(tmpimgdir,filename)
	#    pixbuf.save(filepath,'png')
	#    sdd['fgpixbufs'].append(file(filepath).read())
	#    os.remove(filepath)
	#    count += 1
	return pickle.dumps(sdd)

    def restore(self, sdata):
        # THE BELOW SHOULD WORK BUT DOESN'T
        #zf = StringIO.StringIO(sdata)
	#self.loadfromzip(zf)
        # END OF STUFF THAT DOESN'T WORK
	sdd = pickle.loads(sdata)
	tmpimgdir = os.path.join(self.mdirpath,'tmpimg')
	tmpbgpath = os.path.join(tmpimgdir,'back.png')
	f = file(tmpbgpath,'w')
	f.write(sdd['pngdata'])
	f.close()
	self.setback(tmpbgpath)
	os.remove(tmpbgpath)
	transimgpath = os.path.join(self.iconsdir,TRANSIMG)
	for i in range(len(sdd['fgpixbufpaths'])):
	    filepath = sdd['fgpixbufpaths'][i]
	    if filepath == transimgpath:
	        continue
	    pixbuf = gtk.gdk.pixbuf_new_from_file(filepath)
	    fgpixbuf = pixbuf.scale_simple(BGWIDTH,BGHEIGHT,gtk.gdk.INTERP_BILINEAR)
	    self.fgpixbufs[i] = fgpixbuf
	    if i == 0:
	        self.fgpixbuf = fgpixbuf
	        self.drawmain()
	    scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
	    self.frameimgs[i].set_from_pixbuf(scaled_buf)

    def savefile(self, widget, data=None):
        daction = gtk.FILE_CHOOSER_ACTION_SAVE
        dialog = gtk.FileChooserDialog(title='Save Animation',
                                       action=daction,
                                       buttons=(gtk.STOCK_CANCEL, 
				       gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, 
				       gtk.RESPONSE_OK))
	if self.insugar:
	    dialog.set_current_folder('/home/olpc')
	dialog.set_current_name('cartoon.zip')
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
	if response == gtk.RESPONSE_OK:
	    filepath = dialog.get_filename()
	    zf = file(filepath,'w')
	    self.savetozip(zf)
	elif response == gtk.RESPONSE_CANCEL:
	    pass
	dialog.destroy()

    def savetozip(self, f):
	# print filepath
	#zf = zipfile.ZipFile(filepath,'w')
	zf = zipfile.ZipFile(f,'w')
	# add the background file
	tmpimgdir = os.path.join(self.mdirpath,'tmpimg')
	tmpbgpath = os.path.join(tmpimgdir,'back.png')
	self.bgpixbuf.save(tmpbgpath,'png')
	zf.write(tmpbgpath)
	os.remove(tmpbgpath)
	# add the frames
	count = 1
	for pixbuf in self.fgpixbufs:
	    filename = '%02d.png' % count
	    filepath = os.path.join(tmpimgdir,filename)
	    pixbuf.save(filepath,'png')
	    zf.write(filepath)
	    os.remove(filepath)
	    count += 1
	zf.close()

    def loadfile(self, widget, data=None):
        daction = gtk.FILE_CHOOSER_ACTION_OPEN
        dialog = gtk.FileChooserDialog(title='Select File',
                                       action=daction,
                                       buttons=(gtk.STOCK_CANCEL, 
				       gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, 
				       gtk.RESPONSE_OK))
	if self.insugar:
	    dialog.set_current_folder('/home/olpc')
        dialog.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("Zipfiles")
        #filter.add_mime_type("image/gif")
        filter.add_pattern("*.zip")
        dialog.add_filter(filter)
        response = dialog.run()
	if response == gtk.RESPONSE_OK:
	    filepath = dialog.get_filename()
	    zf = file(filepath,'r')
	    self.loadfromzip(zf)
	elif response == gtk.RESPONSE_CANCEL:
	    pass
	dialog.destroy()

    def loadfromzip(self, f):
	# print filepath
	#zf = zipfile.ZipFile(filepath,'r')
	zf = zipfile.ZipFile(f)
	fnames = zf.namelist()
	framenames = []
	for fname in fnames:
	    if fname[-8:] == 'back.png':
	        backname = fname
	    else:
		framenames.append(fname)
	framenames.sort()
	# set the background
	tmpimgdir = os.path.join(self.mdirpath,'tmpimg')
	tmpbgpath = os.path.join(tmpimgdir,'back.png')
	f = file(tmpbgpath,'w')
	f.write(zf.read(backname))
	f.close()
	self.setback(tmpbgpath)
	os.remove(tmpbgpath)
	self.imgdir = tmpimgdir
	for filepath in framenames:
	    fname = os.path.split(filepath)[1]
            tmpfilepath = os.path.join(tmpimgdir,fname)
	    f = file(tmpfilepath,'w')
	    f.write(zf.read(filepath))
	    f.close()
	zf.close()
	self.loadimages()
	#self.setcharacter()
        # setup the filmstrip frames
        pics = self.getpics(self.imgdir)
	count = 0
	for imgpath in pics:
	    pixbuf = gtk.gdk.pixbuf_new_from_file(imgpath)
	    fgpixbuf = pixbuf.scale_simple(BGWIDTH,BGHEIGHT,gtk.gdk.INTERP_BILINEAR)
	    self.fgpixbufs[count] = fgpixbuf
	    if count == 0:
	        self.fgpixbuf = fgpixbuf
	        self.drawmain()
	    scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
	    self.frameimgs[count].set_from_pixbuf(scaled_buf)
            count += 1
	entries = os.listdir(tmpimgdir)
	for entry in entries:
	    entrypath = os.path.join(tmpimgdir,entry)
	    os.remove(entrypath)

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
	for imgpath in pics[self.imgstartindex:self.imgstartindex+10]:
	    pixbuf = gtk.gdk.pixbuf_new_from_file(imgpath)
	    scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
	    self.posepixbufs.append(pixbuf)
	    self.poseimgpaths.append(imgpath)
            self.images[count].set_from_pixbuf(scaled_buf)
	    count += 1
	for i in range(count,10):
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
	    self.setcharacter()
	    self.drawmain()

    def imgdown(self, widget, data=None):
        pics = self.getpics(self.imgdir)
	if len(pics[self.imgstartindex:]) > 10:
	    self.imgstartindex += 2
	    self.loadimages()
	    self.setcharacter()
	    self.drawmain()

    def gettranspixbuf(self, width=50, height=50):
	transimgpath = os.path.join(self.iconsdir,TRANSIMG)
	pixbuf = gtk.gdk.pixbuf_new_from_file(transimgpath)
	if width == 50 and height == 50:
	    return pixbuf
	scaled_buf = pixbuf.scale_simple(width,height,gtk.gdk.INTERP_BILINEAR)
	return scaled_buf

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

    def changed_cb(self, combobox):
        model = combobox.get_model()
	index = combobox.get_active()
	if index:
	    lang = model[index][0]
	    if lang == 'Espa\xc3\xb1ol':
	        lang = SPANISH
	    if lang in LANG:
	        self.lessonplans.set_label(LANG[lang]['lessonplan'])
		prepare_btn(self.lessonplans)
		if not self.insugar:
		    self.character.set_label(LANG[lang]['character'])
		    prepare_btn(self.character)
		    self.bgbutton.set_label(LANG[lang]['background'])
		    prepare_btn(self.bgbutton)
		    self.soundbutton.set_label(LANG[lang]['sound'])
		    prepare_btn(self.soundbutton)
	    else:
	        print repr(lang)
	return

    def changebuttonlang(self):
	self.lessonplans.set_label(LANG[self.language]['lessonplan'])
	prepare_btn(self.lessonplans)
	self.lang.set_label(self.language)
	prepare_btn(self.lang)
	self.character.set_label(LANG[self.language]['character'])
	prepare_btn(self.character)
	self.bgbutton.set_label(LANG[self.language]['background'])
	prepare_btn(self.bgbutton)
	self.soundbutton.set_label(LANG[self.language]['sound'])
	prepare_btn(self.soundbutton)

    def setlastlanguage(self, widget, data=None):
        li = LANGLIST.index(self.language)
	if li == 0:
	    self.language = LANGLIST[len(LANGLIST)-1]
	else:
	    self.language = LANGLIST[li-1]
	self.changebuttonlang()

    def setnextlanguage(self, widget, data=None):
        li = LANGLIST.index(self.language)
	if li == (len(LANGLIST)-1):
	    self.language = LANGLIST[0]
	else:
	    self.language = LANGLIST[li+1]
	self.changebuttonlang()

    def getdefaultlang(self):
        return 'English'

    def __init__(self,insugar,toplevel_window,mdirpath):
        self.mdirpath = mdirpath
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
	self.insugar = insugar
	self.language = self.getdefaultlang()
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

        self.mpbox = gtk.VBox()

	self.main = gtk.EventBox()
	self.main.show()
        self.main.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
	self.mainbox = gtk.EventBox()
	self.mainbox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.mainbox.set_border_width(5)
	self.mainbox.show()
	self.main.add(self.mainbox)
	self.mpbox.show()
	self.logobox = gtk.HBox(False,0)
	self.logobox.show()
	self.logo = gtk.Image()
	self.logo.show()
	self.logo.set_from_file(os.path.join(self.iconsdir,'logo.png'))
	self.logobox.pack_start(self.logo,False,False,0)
	self.lessonplans = gtk.Button('Lesson Plans')
	self.lessonplans.connect('clicked',self.showlessonplans, None)
	prepare_btn(self.lessonplans)
	self.lessonplans.show()
	self.lpvbox = gtk.VBox()
	self.lpvbox.show()
	self.lpvbox.pack_start(self.lessonplans,True,False,0)
	self.lpoframe = gtk.EventBox()
	self.lpoframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	self.lpoframe.show()
	self.lpframe = gtk.EventBox()
	self.lpframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.lpframe.show()
        self.lpalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	self.lpalign.add(self.lpframe)
	self.lpalign.set_padding(5,0,5,0)
	self.lpalign.show()
	self.lpoframe.add(self.lpalign)
	self.lphbox = gtk.HBox()
	self.lphbox.show()
	self.lphbox.pack_start(self.lpvbox,True,False,0)
	self.lpframe.add(self.lphbox)
	self.logobox.pack_start(self.lpoframe,True,True,0)
        self.langdd = gtk.combo_box_new_text()
	self.langdd.append_text('Language')
	self.langdd.append_text('English')
	self.langdd.append_text(SPANISH)
	self.langdd.connect('changed', self.changed_cb)
	self.langdd.set_active(0)
	self.langdd.show()
	self.langddvbox = gtk.VBox()
	self.langddvbox.show()
	self.langddvbox.pack_start(self.langdd,True,False,0)
	#vvvv LANGUAGE BUTTONS vvvv
	#self.lastlang = gtk.Button()
	#self.lastlang.connect('clicked', self.setlastlanguage, None)
	#llla = gtk.Image()
	#llla.set_from_file(os.path.join(self.iconsdir,'left_arrow.png'))
	#llla.show()
	#self.lastlang.add(llla)
	#prepare_btn(self.lastlang)
	#self.lastlang.show()
	#self.llvbox = gtk.VBox()
	#self.llvbox.show()
	#self.llvbox.pack_start(self.lastlang,True,False,0)
	#self.lang = gtk.Button(self.language)
	#prepare_btn(self.lang)
	#self.lang.show()
	#self.nextlang = gtk.Button()
	#self.nextlang.connect('clicked', self.setnextlanguage, None)
	#nlra = gtk.Image()
	#nlra.set_from_file(os.path.join(self.iconsdir,'right_arrow.png'))
	#nlra.show()
	#self.nextlang.add(nlra)
	#prepare_btn(self.nextlang)
	#self.nextlang.show()
	#self.nlvbox = gtk.VBox()
	#self.nlvbox.show()
	#self.nlvbox.pack_start(self.nextlang,True,False,0)
	#self.langvbox = gtk.VBox()
	#self.langvbox.show()
	#self.langvbox.pack_start(self.lang,True,False,0)
	#^^^^ LANGUAGE BUTTONS^^^^
	self.langoframe = gtk.EventBox()
	self.langoframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	self.langoframe.show()
	self.langframe = gtk.EventBox()
	self.langframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.langframe.show()
	self.langalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	self.langalign.add(self.langframe)
	if not self.insugar:
	    self.langalign.set_padding(5,0,5,0)
	else:
	    self.langalign.set_padding(5,0,5,5)
	self.langalign.show()
	self.langoframe.add(self.langalign)
	self.langhbox = gtk.HBox()
	self.langhbox.show()
	#self.langhbox.pack_start(self.llvbox,True,False,0)
	#self.langhbox.pack_start(self.langvbox,True,False,0)
	#self.langhbox.pack_start(self.nlvbox,True,False,0)
	self.langhbox.pack_start(self.langddvbox,True,False,0)
	self.langframe.add(self.langhbox)
	self.logobox.pack_start(self.langoframe,True,True,0)

        if not self.insugar:
            self.sooframe = gtk.EventBox()
	    self.sooframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	    self.sooframe.show()
	    self.soframe = gtk.EventBox()
	    self.soframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	    self.soframe.show()
	    self.soalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	    self.soalign.add(self.soframe)
	    self.soalign.set_padding(5,0,5,5)
	    self.soalign.show()
	    self.sooframe.add(self.soalign)
	    self.fsvbox = gtk.VBox()
	    self.fsvbox.show()
	    self.fileopen = gtk.Button()
	    openimg = gtk.Image()
	    openimg.set_from_stock(gtk.STOCK_OPEN,gtk.ICON_SIZE_BUTTON)
	    openimg.show()
	    prepare_btn(self.fileopen)
	    self.fileopen.set_label('')
	    self.fileopen.set_image(openimg)
	    self.fileopen.connect('clicked',self.loadfile, None)
	    self.fileopen.show()
	    self.fovbox = gtk.VBox()
	    self.fovbox.show()
	    self.fovbox.pack_start(self.fileopen,True,False,0)
	    self.fohbox = gtk.HBox()
	    self.fohbox.show()
	    self.fohbox.pack_start(self.fovbox,True,False,0)
	    self.filesave = gtk.Button()
	    saveimg = gtk.Image()
	    saveimg.set_from_stock(gtk.STOCK_SAVE,gtk.ICON_SIZE_BUTTON)
	    saveimg.show()
	    prepare_btn(self.filesave)
	    self.filesave.set_label('')
	    self.filesave.set_image(saveimg)
	    self.filesave.connect('clicked',self.savefile, None)
	    self.filesave.show()
	    self.fsvbox.pack_start(self.filesave,True,False,0)
	    self.fohbox.pack_start(self.fsvbox,True,False,0)
	    self.soframe.add(self.fohbox)
	    self.logobox.pack_start(self.sooframe,True,True,0)

	self.mpbox.pack_start(self.logobox,False,False,0)

	self.centerframeborder = gtk.EventBox()
	self.centerframeborder.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	self.centerframeborder.show()
	self.ocenterframe = gtk.EventBox()
	self.ocenterframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.ocenterframe.set_border_width(5)
	self.ocenterframe.show()
	self.centerframeborder.add(self.ocenterframe)
	self.centerframe = gtk.EventBox()
	self.centerframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BACKGROUND))
	self.centerframe.set_border_width(5)
	self.centerframe.show()
	self.ocenterframe.add(self.centerframe)
	self.hbox = gtk.HBox()
	self.hbox.show()
	self.mainbox.add(self.mpbox)
	self.centerframe.add(self.hbox)
	self.mpbox.pack_start(self.centerframeborder,True,True,0)


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
        self.table = gtk.Table(rows=7, columns=2, homogeneous=False)

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
	self.iubhbox.pack_start(self.imgupbutton,True,True,150)
	self.tvbox.pack_start(self.iubhbox,False,False,0)

	self.table.attach(self.imgbuttons[0],0,1,0,1)
	self.table.attach(self.imgbuttons[1],1,2,0,1)
	self.table.attach(self.imgbuttons[2],0,1,1,2)
	self.table.attach(self.imgbuttons[3],1,2,1,2)
	self.table.attach(self.imgbuttons[4],0,1,2,3)
	self.table.attach(self.imgbuttons[5],1,2,2,3)
	self.table.attach(self.imgbuttons[6],0,1,3,4)
	self.table.attach(self.imgbuttons[7],1,2,3,4)
	self.table.attach(self.imgbuttons[8],0,1,4,5)
	self.table.attach(self.imgbuttons[9],1,2,4,5)
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
	self.idbhbox.pack_start(self.imgdownbutton,True,True,150)
	self.tvbox.pack_start(self.idbhbox,False,False,0)
        self.hbox.pack_start(self.tvbox,True,True,0)

	self.imgdir = self.imgdirs[self.imgdirindex]
	self.loadimages()

	self.rightbox = gtk.VBox()
	self.rightbox.show()

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
	for i in range(6):
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
	self.filmstriptopimg = gtk.Image()
	self.filmstriptopimg.set_from_file(os.path.join(self.iconsdir,'filmstrip.png'))
	self.filmstriptopimg.show()
	self.animfilmstrip.pack_start(self.filmstriptopimg,False,False,0)
	self.animfilmstrip.pack_start(self.animhbox,False,False,0)
	self.filmstripbottomimg = gtk.Image()
	self.filmstripbottomimg.set_from_file(os.path.join(self.iconsdir,'filmstrip.png'))
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
        
	self.rightbox.pack_start(self.topvbox,False,False,5)
	self.frame_selected = 0
	self.fbstyle = self.framebuttons[0].get_style()
	self.framebuttons[0].modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(YELLOW))
	self.framebuttons[0].modify_bg(gtk.STATE_PRELIGHT,gtk.gdk.color_parse(YELLOW))

	self.bottomhbox = gtk.HBox()
	self.bottomhbox.show()

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
	self.centervbox.pack_start(self.mfdrawborder,False,False,0)

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
	self.bottomhbox.pack_start(self.centervbox,False,False,0)
	
        self.controlbox = gtk.VBox()
	self.controlbox.show()
	
        # CHARACTER CONTROLS
        self.ccbox = gtk.VBox()
	self.ccbox.show()
	self.cchbox = gtk.HBox()
	self.cchbox.show()
	self.cclbutton = gtk.Button()
	self.cclbutton.connect('clicked',self.lastcharacter,None)
	self.cclbutton.show()
	ccla = gtk.Image()
	ccla.set_from_file(os.path.join(self.iconsdir,'big_left_arrow.png'))
	ccla.show()
	prepare_btn(self.cclbutton)
	self.cclbutton.add(ccla)
	self.cclbvbox = gtk.VBox()
	self.cclbvbox.show()
	self.cclbvbox.pack_start(self.cclbutton,True,False,0)
	self.cchbox.pack_start(self.cclbvbox,True,True,5)
	self.ccibutton = gtk.Button()
	self.ccibutton.show()
	self.ccismall = gtk.Image()
	self.ccismall.show()
	self.cciebox = gtk.EventBox()
	self.cciebox.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BLACK))
	self.cciebox.show()
	self.cciebox.add(self.ccismall)
	self.ccibvbox = gtk.VBox()
	self.ccibvbox.show()
	self.ccibvbox.pack_start(self.cciebox,True,False,0)
	self.cchbox.pack_start(self.ccibvbox,False,False,0)
	self.ccrbutton = gtk.Button()
	self.ccrbutton.connect('clicked',self.nextcharacter,None)
	self.ccrbutton.show()
	ccra = gtk.Image()
	ccra.set_from_file(os.path.join(self.iconsdir,'big_right_arrow.png'))
	ccra.show()
	self.ccrbutton.add(ccra)
	prepare_btn(self.ccrbutton)
	self.ccrbvbox = gtk.VBox()
	self.ccrbvbox.show()
	self.ccrbvbox.pack_start(self.ccrbutton,True,False,0)
	self.cchbox.pack_start(self.ccrbvbox,True,True,5)
	self.ccbox.pack_start(self.cchbox,True,True,0)
	self.charlabel = gtk.Label('')
	self.charlabel.show()
	self.charlabelhbox = gtk.HBox()
	self.charlabelhbox.show()
	self.charlabelhbox.pack_start(self.charlabel,True,False,0)
	self.ccbox.pack_start(self.charlabelhbox,False,False,0)
	if not self.insugar:
	    self.character = gtk.Button('My Character')
	    self.character.connect('clicked',self.getimgdir,None)
	    prepare_btn(self.character)
	    self.character.show()
	    self.characterhbox = gtk.HBox()
	    self.characterhbox.show()
	    self.characterhbox.pack_start(self.character,True,False,0)
	    self.ccbox.pack_start(self.characterhbox,False,False,5)
	self.setcharacter()
	
	
	self.controlbox.pack_start(self.ccbox,False,False,5)

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
	if not self.insugar:
	    self.bgbutton = gtk.Button('My Background')
	    self.bgbutton.connect('clicked',self.getbackgroundfile,None)
	    prepare_btn(self.bgbutton)
	    self.bgbutton.show()
	    self.bgbuttonhbox = gtk.HBox()
	    self.bgbuttonhbox.show()
	    self.bgbuttonhbox.pack_start(self.bgbutton,True,False,0)
	    self.bgbox.pack_start(self.bgbuttonhbox,False,False,5)
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
	if not self.insugar:
	    self.soundbutton = gtk.Button('My Sound')
	    self.soundbutton.connect('clicked',self.getsoundfile,None)
	    prepare_btn(self.soundbutton)
	    self.soundbutton.show()
	    self.soundbuttonhbox = gtk.HBox()
	    self.soundbuttonhbox.show()
	    self.soundbuttonhbox.pack_start(self.soundbutton,True,False,0)
	    self.soundbox.pack_start(self.soundbuttonhbox,False,False,5)
	self.controlbox.pack_start(self.soundbox,False,False,5)
        
	# FINISHING DETAILS
	self.bottomhbox.pack_start(self.controlbox,True,True,10)
	self.rightbox.pack_start(self.bottomhbox,True,True,10)
	self.hbox.pack_start(self.rightbox,True,True,0)

    def main(self):
        gtk.main()

try:
    from sugar.activity import activity
    from sugar.graphics.toolbutton import ToolButton
    from sugar.graphics.objectchooser import ObjectChooser
    from sugar.presence import presenceservice
    from sugar.presence.tubeconn import TubeConnection
    import telepathy
    import telepathy.client
    from dbus import Interface
    from dbus.service import method, signal
    from dbus.gobject_service import ExportedGObject
    
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

    class cartoonbuilderActivity(activity.Activity):
        def __init__(self, handle):
            activity.Activity.__init__(self,handle)
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
            outerframe = gtk.EventBox()
	    outerframe.modify_bg(gtk.STATE_NORMAL,gtk.gdk.color_parse(BUTTON_BACKGROUND))
            outerframe.show()
            innerframe = gtk.EventBox()
            innerframe.show()
            ifalign = gtk.Alignment(1.0,1.0,1.0,1.0)
	    ifalign.add(innerframe)
	    ifalign.set_padding(10,10,30,30) # top,bottom,left,right
	    ifalign.show()
            #innerframe.set_border_width(150)
            outerframe.add(ifalign)
            innerframe.add(self.app.main)
            self.set_canvas(outerframe)

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


        def destroy_cb(self, data=None):
            return True

	def read_file(self, filepath):
	    zf = file(filepath,'r')
	    self.app.loadfromzip(zf)

	def write_file(self, filepath):
	    zf = file(filepath,'w')
	    self.app.savetozip(zf)

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
