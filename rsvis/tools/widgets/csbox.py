# ===========================================================================
#   csbox.py ----------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
from rsvis.tools.widgets import combobox, settingsbox, buttonbox

from tkinter import *

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class CSBox(Frame):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self,
        parent,
        bbox=list(),
        cbox=list(),
        sbox=list(),
        button="",
        **kwargs
    ):
        super(CSBox, self).__init__(parent, **kwargs)

        self._bbox = buttonbox.ButtonBox(self, bbox=bbox, **kwargs)
        self._bbox.pack(side=TOP, fill=X)

        self._cbox = combobox.ComboBox(self, cbox=cbox, **kwargs)
        self._cbox.pack(side=TOP, fill=X)

        self._sbox = settingsbox.SettingsBox(self, sbox=sbox, **kwargs)
        self._sbox.pack(side=TOP, fill=X)

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get(self, index=0):
        return self.get_list()[index]

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def set_label(self, choice, index=0):
    #     self._entries[index][1].set(choice)

    # #   method --------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # def get_label(self, index=0):
    #     return self._entries[index][1]
    
    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_list(self):
        return self._cbox.get_list() + self._sbox.get_list()

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def get_dict(self):
        entries = dict()
        entries.update(self._cbox.get_dict())
        entries.update(self._sbox.get_dict())
        return entries        