#!/usr/bin/env python3
"""
This file is part of gnome-search-lastpass.

gnome-search-lastpass is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

gnome-search-lastpass is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import subprocess
import sys

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk, GLib

class ErrorWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Error getting lastpass data")
        self.set_default_size(100, 50)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(box)

        label = Gtk.Label(label="There was an error getting lastpass data")
        label.set_line_wrap(wrap=True)
        box.add(label)

        button = Gtk.Button.new_with_label("Ok")
        button.connect("clicked", Gtk.main_quit)
        box.add(button)

class LastPassWindow(Gtk.Window):
    def __init__(self, entry):
        Gtk.Window.__init__(self, title="Lastpass entry")
        self.set_default_size(300, 200)
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.entry = entry

        box_main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(box_main)

        box_entries = Gtk.Grid()
        box_main.add(box_entries)

        url_frame = Gtk.Frame(label="URL")
        box_entries.attach(url_frame, 1, 1, 2, 1)
        url = Gtk.Entry()
        url_frame.add(url)
        url.props.text = entry['url']
        url.props.editable = False

        username_frame = Gtk.Frame(label="Username")
        box_entries.attach(username_frame, 1, 2, 1, 1)
        username = Gtk.Entry()
        username_frame.add(username)
        username.props.text = entry['username']
        username.props.editable = False

        password_frame = Gtk.Frame(label="Password")
        box_entries.attach(password_frame, 2, 2, 1, 1)
        password = Gtk.Entry()
        password_frame.add(password)
        password.props.text = entry['password']
        password.props.editable = False
        password.set_visibility(False)
        password.props.input_purpose = Gtk.InputPurpose.PASSWORD

        note_frame = Gtk.Frame(label="Note")
        box_entries.attach(note_frame, 1, 3, 2, 1)
        note = Gtk.TextView()
        note_frame.add(note)
        note.set_wrap_mode(wrap_mode=Gtk.WrapMode.NONE)
        note.props.buffer.set_text(text=entry['note'])
        note.props.editable = False

        button_box = Gtk.ButtonBox(spacing=6)
        box_main.add(button_box)

        copy_url_button = Gtk.Button.new_with_label("Copy URL")
        button_box.add(copy_url_button)
        copy_url_button.connect("clicked", self.copy, "url")

        copy_username_button = Gtk.Button.new_with_label("Copy username")
        button_box.add(copy_username_button)
        copy_username_button.connect("clicked", self.copy, "username")

        copy_password_button = Gtk.Button.new_with_label("Copy password")
        button_box.add(copy_password_button)
        copy_password_button.connect("clicked", self.copy, "password")

        copy_note_button = Gtk.Button.new_with_label("Copy note")
        button_box.add(copy_note_button)
        copy_note_button.connect("clicked", self.copy, "note")

    def copy(self, callback, item):
        self.clipboard.set_text(self.entry[item], -1)
        self.hide()
        GLib.timeout_add(100, Gtk.main_quit)

def main():
    if len(sys.argv) != 2:
        print(f"Usage {sys.argv[0]} lastpassid")
        sys.exit(1)

    ret = subprocess.run(["lpass", "show", "--json", sys.argv[1]], encoding='utf-8', timeout=30, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if ret.returncode == 0:
        try:
            entry = json.loads(ret.stdout)
            window = LastPassWindow(entry[0])
        except Exception as e:
            print(e)
            window = ErrorWindow()
    else:
        window = ErrorWindow()

    window.connect("destroy", Gtk.main_quit)
    window.show_all()

    Gtk.main()

if __name__ == "__main__":
    main()
