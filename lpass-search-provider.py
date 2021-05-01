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

import subprocess
import time

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service
from gi.repository import GLib
from fuzzywuzzy import process, fuzz

DBusGMainLoop(set_as_default=True)

# Convenience shorthand for declaring dbus interface methods.
# s.b.n. -> search_bus_name
search_bus_name = 'org.gnome.Shell.SearchProvider2'
sbn = dict(dbus_interface=search_bus_name)

class SearchPassService(dbus.service.Object):
    """ The search daemon.
    This service is started through DBus activation by calling the
    :meth:`Enable` method, and stopped with :meth:`Disable`.
    """
    bus_name = 'name.haavard.Lastpass.SearchProvider'

    _object_path = '/' + bus_name.replace('.', '/')

    def __init__(self):
        self.session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self._object_path)
        self.cache = {'timestamp': 0 }

    @dbus.service.method(in_signature='sasu', **sbn)
    def ActivateResult(self, id, terms, timestamp):
        subprocess.run([
            "lpass-show-copy.py",
            id
            ])

    @dbus.service.method(in_signature='as', out_signature='as', **sbn)
    def GetInitialResultSet(self, terms):
        return self.get_result_set(terms)

    @dbus.service.method(in_signature='as', out_signature='aa{sv}', **sbn)
    def GetResultMetas(self, ids):
        cache = self._get_lastpass_cache()

        if self.cache is None:
            return []
        result = []

        for id in ids:
            if not id in cache['entries']:
                continue
            entry = cache['entries'][id]
            elem = dict(id=id, name=cache['entries'][id], gicon="lastpass")
            description = []

            if id in cache['urls']:
                description.append(cache['urls'][id])

            if id in cache['usernames']:
                description.append("User: {}".format(cache['usernames'][id]))

            if len(description) > 0:
                elem['description'] = "\n".join(description)
            result.append(elem)

        return result

    @dbus.service.method(in_signature='asas', out_signature='as', **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        return self.get_result_set(new_terms)

    @dbus.service.method(in_signature='asu', terms='as', timestamp='u', **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass

    def get_result_set(self, terms):
        cache = self._get_lastpass_cache()

        if cache is None:
            return []
        name = ''.join(terms)
        entries = [(e[2], e[1], e[0]) for e in process.extract(name, cache['entries'], limit=5, scorer=fuzz.partial_ratio)]
        usernames = [(e[2], e[1], e[0]) for e in process.extract(name, cache['usernames'], limit=5, scorer=fuzz.ratio)]
        urls = [(e[2], e[1], e[0]) for e in process.extract(name, cache['urls'], limit=5, scorer=fuzz.ratio)]

        return [e[0] for e in sorted(entries + usernames + urls, key=lambda x: x[1], reverse=True)][0:4]

    def _get_lastpass_cache(self):
        if int(time.time()) - self.cache['timestamp'] < 60:
            return self.cache

        self.cache['entries'] = {}
        self.cache['usernames'] = {}
        self.cache['urls'] = {}
        result = subprocess.run(['lpass', 'ls', '--format', '%ai;%/as%/ag%an;%au;%al'], encoding='utf-8', timeout=10, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        if result.returncode != 0:
            return None
        self.cache['timestamp'] = int(time.time())

        for line in result.stdout.split("\n"):
            (id, name, username, url) = line.strip().split(';')
            self.cache['entries'][id] = name

            if len(username) > 0:
                self.cache['usernames'][id] = username

            if len(url) > 0 and url != 'http://' and url != 'https://':
                self.cache['urls'][id] = url

        return self.cache

def main():
    SearchPassService()
    GLib.MainLoop().run()

if __name__ == '__main__':
    main()
