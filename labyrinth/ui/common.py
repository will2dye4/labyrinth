"""Subclasses of the predefined tk classes to customize the look of the UI."""

from typing import Any, Callable
import tkinter as tk

from labyrinth.ui.colors import BACKGROUND_COLOR, FONT, PATH_COLOR, TEXT_COLOR


LEFT_CLICK = '<Button-1>'
MOTION = '<Motion>'


class Checkbutton(tk.Checkbutton):
    """Checkbutton subclass."""

    def __init__(self, parent: Any, **kwargs) -> None:
        """Initialize a Checkbutton."""
        super().__init__(parent, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=FONT, padx=10, **kwargs)


class Entry(tk.Entry):
    """Entry subclass."""

    def __init__(self, parent: Any, **kwargs) -> None:
        """Initialize an Entry."""
        super().__init__(parent, font=FONT, **kwargs)


class Frame(tk.Frame):
    """Frame subclass."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a Frame."""
        super().__init__(*args, bg=BACKGROUND_COLOR, **kwargs)


class Label(tk.Label):
    """Label subclass."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize a Label."""
        fg = kwargs.pop('fg', TEXT_COLOR)
        super().__init__(*args, bg=BACKGROUND_COLOR, fg=fg, font=FONT, **kwargs)


class LabelButton(Label):
    """LabelButton is a button in the UI implemented using a Label."""

    def __init__(self, parent: Any, text: str, click_handler: Callable[[tk.Event], None], **kwargs):
        """Initialize a LabelButton."""
        super().__init__(parent, text=text, fg=PATH_COLOR, padx=10, pady=10, bd=3, relief=tk.GROOVE,
                         cursor='hand2', **kwargs)
        self.bind(LEFT_CLICK, click_handler)


class Radiobutton(tk.Radiobutton):
    """Radiobutton subclass."""

    def __init__(self, parent: Any, **kwargs) -> None:
        """Initialize a Radiobutton."""
        super().__init__(parent, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=FONT, padx=5, pady=5,
                         selectcolor=PATH_COLOR, **kwargs)


class Scale(tk.Scale):
    """Scale subclass."""

    def __init__(self, parent: Any, **kwargs) -> None:
        """Initialize a Scale."""
        super().__init__(parent, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, **kwargs)
