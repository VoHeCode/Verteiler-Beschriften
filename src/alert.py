#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""
module docstring - short summary

If the description is long, the first line should be a short summary that makes sense on its own,
separated from the rest by a newline
"""

__version__ = "1.0.0"
__author__ = "Author 1, Author 2, Author 3"  # only code writers
__email__ = "author@bogusproject.com"
__maintainer__ = "Maintainer 1"  # should be the person who will fix bugs and make improvements
__copyright__ = "Copyright 2019, The Bogus Project"
__license__ = "GPL"
__status__ = "Production"  # Prototype, Development or Production
__credits__ = ["name 1", "name 2"]  # also include contributors that wrote no code

# --------------------------------------------------------------------------------
import flet as ft


def main(page: ft.Page):
    page.title = "AlertDialog examples"

    dialog = ft.AlertDialog(
        title=ft.Text("Hello"),
        content=ft.Text("You are notified!"),
        alignment=ft.Alignment.CENTER,
        on_dismiss=lambda e: print("Dialog dismissed!"),
        title_padding=ft.Padding.all(25),
    )

    modal_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to delete all those files?"),
        actions=[
            ft.TextButton("Yes", on_click=lambda e: page.pop_dialog()),
            ft.TextButton("No", on_click=lambda e: page.pop_dialog()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )

    page.add(
        ft.Button(
            content="Open dialog",
            on_click=lambda e: page.show_dialog(dialog),
        ),
        ft.Button(
            content="Open modal dialog",
            on_click=lambda e: page.show_dialog(modal_dialog),
        ),
    )


if __name__ == "__main__":
    ft.run(main)
