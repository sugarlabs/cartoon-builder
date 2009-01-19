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

class Char:
    id = 0
    pixbuf = None #gtk.gdk.Pixbuf()

def themes():
    return [Char()]


"""
        pics = self.getpics(self.imgdir)
        pixbuf = gtk.gdk.pixbuf_new_from_file(pics[self.imgstartindex])
        scaled_buf = pixbuf.scale_simple(IMGWIDTH,IMGHEIGHT,gtk.gdk.INTERP_BILINEAR)
        self.ccismall.set_from_pixbuf(scaled_buf)
        self.charlabel.set_label(os.path.split(self.imgdir)[1])


    def restore(self, sdata):
        # THE BELOW SHOULD WORK BUT DOESN'T
        #zf = StringIO.StringIO(sdata)
        #self.loadfromzip(zf)
        # END OF STUFF THAT DOESN'T WORK
        sdd = pickle.loads(sdata)
        tmpbgpath = os.path.join(TMPDIR,'back.png')
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
        tmpbgpath = os.path.join(TMPDIR,'back.png')
        f = file(tmpbgpath,'w')
        f.write(zf.read(backname))
        f.close()
        self.setback(tmpbgpath)
        os.remove(tmpbgpath)
        self.imgdir = TMPDIR
        for filepath in framenames:
            fname = os.path.split(filepath)[1]
            tmpfilepath = os.path.join(TMPDIR,fname)
            f = file(tmpfilepath,'w')
            f.write(zf.read(filepath))
            f.close()
        zf.close()
        self.loadimages()
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
        entries = os.listdir(TMPDIR)
        for entry in entries:
            entrypath = os.path.join(TMPDIR,entry)
            os.remove(entrypath)

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


"""
