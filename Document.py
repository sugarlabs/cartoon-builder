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

import Theme

def load(filepath):
    pass

def save(filepath):
    pass

def orig(index):
    return gtk.gdk.pixbuf_new_from_file(
            Theme.path('images/pics/Elephant/bigelephant0.gif'))

def thumb(index):
    return gtk.gdk.pixbuf_new_from_file_at_size(
            Theme.path('images/pics/Elephant/bigelephant0.gif'),
            Theme.THUMB_SIZE, Theme.THUMB_SIZE)

def clean(index):
    pass

def stamp(index, pixbuf):
    pass

"""
import zipfile
import StringIO

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



    def savetozip(self, f):
        # print filepath
        #zf = zipfile.ZipFile(filepath,'w')
        zf = zipfile.ZipFile(f,'w')
        # add the background file
        tmpbgpath = os.path.join(TMPDIR,'back.png')
        self.bgpixbuf.save(tmpbgpath,'png')
        zf.write(tmpbgpath)
        os.remove(tmpbgpath)
        # add the frames
        count = 1
        for pixbuf in self.fgpixbufs:
            filename = '%02d.png' % count
            filepath = os.path.join(TMPDIR,filename)
            pixbuf.save(filepath,'png')
            zf.write(filepath)
            os.remove(filepath)
            count += 1
        zf.close()


"""
