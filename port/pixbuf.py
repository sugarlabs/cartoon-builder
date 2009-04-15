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

"""gtk.gdk.Pixbuf extensions"""

import os
import cStringIO
import tempfile
import gtk

def to_file(pixbuf):
    """Convert pixbuf object to file object"""

    def push(pixbuf, buffer):
        buffer.write(pixbuf)

    buffer = cStringIO.StringIO()
    pixbuf.save_to_callback(push, 'png', user_data=buffer)
    buffer.seek(0)

    return buffer

def to_str(pixbuf):
    """Convert pixbuf object to string"""
    return to_file(pixbuf).getvalue()

def from_str(str):
    """Convert string to pixbuf object"""

    file_d, path = tempfile.mkstemp()

    file_o = os.fdopen(file_d, 'w')
    file_o.write(str)
    file_o.close()

    out = gtk.gdk.pixbuf_new_from_file(path)
    os.unlink(path)

    return out
