"""Small input popups for interacting with TODO widgets."""

from __future__ import annotations

from typing import Any, Callable, Optional

import urwid
from urwid_readline import ReadlineEdit

from zulipterminal.config.keys import is_command_key
from zulipterminal.urwid_types import urwid_Size


class TodoTextInputPopup(urwid.Frame):
    """A minimal popup with a single-line input and Enter/Esc handling.

    This intentionally does not depend on `ui_tools.views` to avoid circular imports.
    """

    def __init__(
        self,
        controller: Any,
        *,
        title: str,
        prompt: str,
        initial_text: str = "",
        on_submit: Callable[[str], None],
        requested_width: int = 62,
        footer_text: Optional[str] = None,
    ) -> None:
        self.controller = controller
        self.title = title
        self._on_submit = on_submit

        popup = self

        class _SubmitEdit(ReadlineEdit):
            def keypress(self, size: urwid_Size, key: str) -> Any:
                if is_command_key("EXIT_POPUP", key):
                    popup.controller.exit_popup()
                    return None
                normalized = key.strip().lower()
                if (
                    normalized in {"enter", "return", "ctrl m", "ctrl j", "activate"}
                    or normalized.endswith(" enter")
                    or normalized.endswith(" return")
                    or normalized.endswith("enter")
                    or normalized.endswith("return")
                    or normalized.endswith(" activate")
                    or normalized.endswith("activate")
                ):
                    text = self.edit_text.strip()
                    popup.controller.exit_popup()
                    popup._on_submit(text)
                    return None
                return super().keypress(size, key)

        self._edit = _SubmitEdit(f"{prompt} ", edit_text=initial_text)
        widgets = [self._edit]

        body = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
        footer = urwid.Text(footer_text) if footer_text else None

        max_cols, max_rows = controller.maximum_popup_dimensions()
        self.width = min(max_cols, requested_width)

        height = sum(widget.rows((self.width,)) for widget in widgets)
        if footer is not None:
            height += footer.rows((self.width,))
        self.height = min(max_rows, height)

        super().__init__(body=body, footer=footer)

        # Put cursor at end.
        self._edit.set_edit_pos(len(self._edit.edit_text))

    def keypress(self, size: urwid_Size, key: str) -> Optional[str]:
        return super().keypress(size, key)
