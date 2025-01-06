"""Tooltip for the app"""

from idlelib.tooltip import Hovertip
import tkinter as tk

# Shoutout to idlelib.tooltip
class Tooltip(Hovertip):
    """
    The tooltip.
    """
    def __init__(self, anchor_widget, text):
        super().__init__(anchor_widget, text, hover_delay=10)

    def showtip(self):
        """
        Display the tooltip.

        source: https://stackoverflow.com/questions/67241085/python-tkinter-tooltip-on-modal-window
        """
        if self.tipwindow:
            return
        self.tipwindow = tw = tk.Toplevel(self.anchor_widget)
        # show no border on the top level window
        tw.wm_overrideredirect(1)
        # make it on top
        tw.wm_attributes("-topmost", True)
        try:
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass

        self.position_window()
        self.showcontents()
        self.tipwindow.update_idletasks()
        self.tipwindow.lift()
