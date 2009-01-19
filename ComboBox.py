import pygtk
import gtk

from Theme import *
from sugar.graphics.combobox import *

class BigComboBox(ComboBox):

    def __init__(self):
        ComboBox.__init__(self)

        self.set_name('fubar')

    
    def append_item(self, action_id, text = None, icon_name = None, size = None,
            pixbuf = None):

        if not self._icon_renderer and (icon_name or pixbuf):
            self._icon_renderer = gtk.CellRendererPixbuf()

            settings = self.get_settings()
            w, h = gtk.icon_size_lookup_for_settings(settings, gtk.ICON_SIZE_MENU)
            self._icon_renderer.props.stock_size = w

            self.pack_start(self._icon_renderer, False)
            self.add_attribute(self._icon_renderer, 'pixbuf', 2)

        if not self._text_renderer and text:
            self._text_renderer = gtk.CellRendererText()
            self.pack_end(self._text_renderer, True)
            self.add_attribute(self._text_renderer, 'text', 1)

        if not pixbuf:
            if icon_name:
                if not size:
                    size = gtk.ICON_SIZE_LARGE_TOOLBAR
                    width, height = gtk.icon_size_lookup(size)
                else:
                    width, height = size
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon_name,
                        width, height)
            else:
                pixbuf = None

        self._model.append([action_id, text, pixbuf, False])
