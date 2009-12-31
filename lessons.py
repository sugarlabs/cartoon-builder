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

import os
import gtk
import locale
import logging
from glob import glob

import theme

THEMES = []

class Lesson:
    def __init__(self, index, filename):
        self.index = index
        self.name = os.path.splitext(os.path.basename(filename).lstrip(
                '.-_1234567890').replace('_', ' '))[0]
        self.text = file(filename, 'r').read()

    def change(self):
        View.notebook.set_current_page(self.index)

class View(gtk.EventBox):
    notebook = None

    def __init__(self):
        gtk.EventBox.__init__(self)

        View.notebook = gtk.Notebook()
        View.notebook.props.show_border = False
        View.notebook.props.show_tabs = False
        self.add(View.notebook)

        for i in THEMES:
            view = gtk.TextView()
            view.get_buffer().set_text(i.text)
            view.set_wrap_mode(gtk.WRAP_WORD)
            view.set_editable(False)

            view_box = gtk.EventBox()
            view_box.add(view)
            view_box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(theme.WHITE))
            view_box.props.border_width = 10

            border_box = gtk.EventBox()
            border_box.add(view_box)
            border_box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse(theme.WHITE))

            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
            scrolled_window.add_with_viewport(border_box)

            View.notebook.append_page(scrolled_window)

        self.show_all()

_locale = locale.getdefaultlocale()[0]
_lang = _locale and _locale.split('_')[0] or 'en'

if not os.path.isdir(theme.path('lessons', _lang)):
    logging.info('Cannot find lessons for language %s, thus use en' % _lang)
    _lang = 'en'

for i, filename in enumerate(sorted(glob(theme.path('lessons', _lang, '*')))):
    THEMES.append(Lesson(i, filename))
