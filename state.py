#!/usr/bin/env python3
# coding=utf-8

"""State Helper"""

##########################################
# main class


class State(object):
    """State."""

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        if value:
            self._enter()
        else:
            self._leave()

    def __init__(self, name, enter=None, update=None, leave=None):
        super(State, self).__init__()
        self._active = False
        self.name = name
        self.enter = enter
        self.update = update
        self.leave = leave

    def _enter(self):
        """enter state."""
        if not self._active:
            self._active = True
            if self.enter:
                self.enter()

    def _leave(self):
        """leave state."""
        if self._active:
            self._active = False
            if self.leave:
                self.leave()

    def _update(self):
        """update state."""
        if self._active:
            if self.update:
                self.update()
