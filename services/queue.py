"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Queue Manager

 Keeps the play queue, current position, shuffle/repeat
 modes, and drives the local MPVPlayer.

 Version : 0.2
===========================================================
"""

import random
import threading

from core.player import player
from services.airsonic_service import service


class QueueManager:

    def __init__(self):
        self.tracks = []
        self.index = -1

        self.shuffle = False
        self.repeat = "off"  # off | all | one
        self.radio = False

        self._shuffle_order = []
        self._lock = threading.Lock()

        player.on_track_end = self._handle_track_end

    # ==========================
    # QUEUE CONTROL
    # ==========================

    def set_queue(self, tracks, start_index=0):
        with self._lock:
            self.tracks = list(tracks)
            self.index = (
                max(0, min(start_index, len(self.tracks) - 1))
                if self.tracks else -1
            )
            self._rebuild_shuffle()

        self._play_current()

    def add(self, track):
        start = False

        with self._lock:
            self.tracks.append(track)
            self._rebuild_shuffle()

            if self.index == -1:
                self.index = len(self.tracks) - 1
                start = True

        if start:
            self._play_current()

    def clear(self):
        with self._lock:
            self.tracks = []
            self.index = -1
            self._shuffle_order = []

        player.stop()

    def current(self):
        if 0 <= self.index < len(self.tracks):
            return self.tracks[self.index]
        return None

    # ==========================
    # MODES
    # ==========================

    def toggle_shuffle(self):
        with self._lock:
            self.shuffle = not self.shuffle
            self._rebuild_shuffle()

        return self.shuffle

    def cycle_repeat(self):
        order = ["off", "all", "one"]
        self.repeat = order[(order.index(self.repeat) + 1) % len(order)]
        return self.repeat

    def toggle_radio(self):
        self.radio = not self.radio
        return self.radio

    # ==========================
    # TRANSPORT
    # ==========================

    def next(self, user_initiated=True):
        with self._lock:
            if not self.tracks:
                return

            if self.repeat == "one" and not user_initiated:
                target = self.index
            else:
                target = self._advance(self.index, 1)

            last_track = (
                self.tracks[-1]
                if target is None and self.radio
                else None
            )

        if last_track and self._extend_radio(last_track):
            with self._lock:
                target = self._advance(self.index, 1)

        with self._lock:
            if target is None:
                self.index = -1
                stop = True
            else:
                self.index = target
                stop = False

        if stop:
            player.stop()
        else:
            self._play_current()

    def _extend_radio(self, last_track):
        songs = service.get_similar(last_track.get("artistId"), limit=15)

        if not songs:
            return False

        with self._lock:
            self.tracks.extend(songs)
            self._rebuild_shuffle()

        return True

    def previous(self):
        with self._lock:
            if not self.tracks:
                return

            target = self._advance(self.index, -1)
            self.index = target if target is not None else 0

        self._play_current()

    def _handle_track_end(self):
        self.next(user_initiated=False)

    def _advance(self, index, step):
        if not self.tracks:
            return None

        n = len(self.tracks)

        if self.shuffle:
            order = self._shuffle_order
            pos = order.index(index) + step if index in order else 0

            if pos >= n or pos < 0:
                if self.repeat == "all":
                    pos %= n
                else:
                    return None

            return order[pos]

        new_index = index + step

        if new_index >= n or new_index < 0:
            if self.repeat == "all":
                return new_index % n
            return None

        return new_index

    def _rebuild_shuffle(self):
        order = list(range(len(self.tracks)))
        random.shuffle(order)
        self._shuffle_order = order

    def _play_current(self):
        track = self.current()

        if track and track.get("stream"):
            player.load(track["stream"])

    # ==========================
    # STATE
    # ==========================

    def get_state(self):
        state = player.get_state()

        state["queue_length"] = len(self.tracks)
        state["index"] = self.index
        state["shuffle"] = self.shuffle
        state["repeat"] = self.repeat
        state["radio"] = self.radio
        state["track"] = self.current()
        state["tracks"] = self.tracks

        return state


queue = QueueManager()
