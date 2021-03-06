#!/usr/bin/env python
# QTvcp Tool Bar Action
#
# Copyright (c) 2019 Chris Morley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from qtvcp.core import Status, Action, Info
from qtvcp.widgets.dialog_widget import LcncDialog as Dialog
from qtvcp.lib.aux_program_loader import Aux_program_loader
from qtvcp import logger

# Instantiate the libraries with global reference
# INFO holds INI file details
# STATUS gives us status messages from linuxcnc
# LOG is for running code logging
STATUS = Status()
ACTION = Action()
INFO = Info()
AUX_PRGM = Aux_program_loader()
LOG = logger.getLogger(__name__)
_DIALOG = Dialog()

# Set the log level for this module
# LOG.setLevel(logger.INFO) # One of DEBUG, INFO, WARNING, ERROR, CRITICAL

CONFIGDIR = os.environ['CONFIG_DIR']

class ToolBarActions():
    def __init__(self, path=None):
        self.path = path
        self.recentNum = 0
        self.gcode_properties = None
        self.maxRecent = 5
        self.viewActiongroup = QtWidgets.QActionGroup(None)

    def configure_action(self, widget, action, extFunction = None):
        action = action.lower()
        function = None

        def homed_on_loaded_test():
            return (STATUS.machine_is_on()
                    and (STATUS.is_all_homed() or INFO.NO_HOME_REQUIRED)
                    and STATUS.is_file_loaded())
        def homed_on_test():
            return (STATUS.machine_is_on()
                    and (STATUS.is_all_homed() or INFO.NO_HOME_REQUIRED))
        def update_properties(d):
            self.gcode_properties = d

        if action == 'estop':
            STATUS.connect('state-estop', lambda w: widget.setChecked(True))
            STATUS.connect('state-estop-reset', lambda w: widget.setChecked(False))
            function = (self.actOnEstop)
        elif action == 'power':
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop-reset', lambda w: widget.setEnabled(True))
            STATUS.connect('state-estop', lambda w: widget.setChecked(False))
            function = (self.actOnPower)
        elif action == 'load':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(STATUS.machine_is_on()))
            STATUS.connect('interp-run', lambda w: widget.setEnabled(False))
            STATUS.connect('all-homed', lambda w: widget.setChecked(True))
            function = (self.actOnLoad)
        elif action == 'reload':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(STATUS.machine_is_on()))
            STATUS.connect('interp-run', lambda w: widget.setEnabled(False))
            STATUS.connect('all-homed', lambda w: widget.setChecked(True))
            function = (self.actOnReload)
        elif action == 'gcode_properties':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(STATUS.machine_is_on()))
            STATUS.connect('interp-run', lambda w: widget.setEnabled(False))
            STATUS.connect('all-homed', lambda w: widget.setChecked(True))
            STATUS.connect('graphics-gcode-properties', lambda w, d: update_properties(d))
            function = (self.actOnProperties)
        elif action == 'run':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(homed_on_test()))
            STATUS.connect('interp-run', lambda w: widget.setEnabled(False))
            STATUS.connect('all-homed', lambda w: widget.setEnabled(True))
            STATUS.connect('not-all-homed', lambda w, data: widget.setEnabled(False))
            STATUS.connect('interp-paused', lambda w: widget.setEnabled(True))
            STATUS.connect('file-loaded', lambda w, f: widget.setEnabled(True))
            function = (self.actOnRun)
        elif action == 'pause':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(homed_on_test()))
            STATUS.connect('all-homed', lambda w: widget.setEnabled(True))
            STATUS.connect('not-all-homed', lambda w, data: widget.setEnabled(False))
            STATUS.connect('program-pause-changed', lambda w, state: widget.setChecked(state))
            function = (self.actOnPause)
        elif action == 'abort':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(homed_on_test()))
            STATUS.connect('all-homed', lambda w: widget.setEnabled(True))
            STATUS.connect('not-all-homed', lambda w, data: widget.setEnabled(False))
            function = (self.actOnAbort)
        elif action == 'block_delete':
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('mode-mdi', lambda w: widget.setEnabled(True))
            STATUS.connect('mode-manual', lambda w: widget.setEnabled(True))
            STATUS.connect('mode-auto', lambda w: widget.setEnabled(False))
            STATUS.connect('block-delete-changed', lambda w, data: widget.setChecked(data))
            function = (self.actOnBlockDelete)
        elif action == 'optional_stop':
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('mode-mdi', lambda w: widget.setEnabled(True))
            STATUS.connect('mode-manual', lambda w: widget.setEnabled(True))
            STATUS.connect('mode-auto', lambda w: widget.setEnabled(False))
            function = (self.actOnOptionalStop)
        elif action == 'home_submenu':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(STATUS.machine_is_on()))
            STATUS.connect('interp-run', lambda w: widget.setEnabled(False))
            self.addHomeActions(widget)
            function = None
        elif action == 'load_calibration':
            function = (self.actOnLoadCalibration)
        elif action == 'load_halmeter':
            function = (self.actOnLoadHalmeter)
        elif action == 'load_halshow':
            function = (self.actOnLoadHalshow)
        elif action == 'load_status':
            function = (self.actOnLoadStatus)
        elif action == 'load_halscope':
            function = (self.actOnLoadHalscope)
        elif action == 'about':
            function = (self.actOnAbout)
        elif action == 'zoom_in':
            function = (self.actOnZoomIn)
        elif action == 'zoom_out':
            function = (self.actOnZoomOut)
        elif action == 'view_x':
            self.viewActiongroup.addAction(widget)
            self.viewActiongroup.setExclusive(True)
            function = (self.actOnViewX)
        elif action == 'view_y':
            self.viewActiongroup.addAction(widget)
            self.viewActiongroup.setExclusive(True)
            function = (self.actOnViewY)
        elif action == 'view_y2':
            self.viewActiongroup.addAction(widget)
            self.viewActiongroup.setExclusive(True)
            function = (self.actOnViewY2)
        elif action == 'view_z':
            self.viewActiongroup.addAction(widget)
            self.viewActiongroup.setExclusive(True)
            function = (self.actOnViewZ)
        elif action == 'view_z2':
            self.viewActiongroup.addAction(widget)
            self.viewActiongroup.setExclusive(True)
            function = (self.actOnViewZ2)
        elif action == 'view_p':
            self.viewActiongroup.addAction(widget)
            self.viewActiongroup.setExclusive(True)
            function = (self.actOnViewp)
        elif action == 'view_clear':
            function = (self.actOnViewClear)
        elif action == 'quit':
            function = (self.actOnQuit)
        elif action == 'recent_submenu':
            STATUS.connect('state-off', lambda w: widget.setEnabled(False))
            STATUS.connect('state-estop', lambda w: widget.setEnabled(False))
            STATUS.connect('interp-idle', lambda w: widget.setEnabled(STATUS.machine_is_on()))
            STATUS.connect('interp-run', lambda w: widget.setEnabled(False))
            STATUS.connect('all-homed', lambda w: widget.setEnabled(True))
            STATUS.connect('file-loaded', lambda w, d: self.updateRecent(widget, d))
            function = None

        else:
            LOG.warning('Unrecogzied action command: {}'.format(action))

        # Call an external function when triggered. If it's checkable; add state
        if extFunction:
            if widget.isCheckable():
                widget.triggered.connect(lambda state: extfunction(widget, state))
            else:
                widget.triggered.connect(lambda: extFunction(widget))

        # Call a function when triggered. If it's checkable; add state
        elif function:
            if widget.isCheckable():
                widget.triggered.connect(lambda state: function(widget, state))
            else:
                widget.triggered.connect(lambda: function(widget))

    def actOnEstop(self, widget, state):
        ACTION.SET_ESTOP_STATE(state)

    def actOnPower(self, widget, state):
        ACTION.SET_MACHINE_STATE(state)

    def actOnLoad(self,widget, state=None):
        STATUS.emit('load-file-request')

    def actOnReload(self,widget, state=None):
        STATUS.emit('reload-display')

    def actOnProperties(self,widget, state=None):
        mess = ''
        if self.gcode_properties:
            for i in self.gcode_properties:
                mess +='<b>%s</b>: %s<br>'%( i, self.gcode_properties[i])
        else:
            mess = 'No properties to display'
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(mess)
        msg.setWindowTitle("Gcode Properties")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.show()
        retval = msg.exec_()

    def actOnRun(self,widget, state=None):
        ACTION.RUN()
    def actOnPause(self,widget, state=None):
        ACTION.PAUSE()

    def actOnAbort(self,widget, state=None):
        ACTION.ABORT()

    def actOnBlockDelete(self, state):
        if state:
            ACTION.SET_BLOCK_DELETE_ON()
        else:
            ACTION.SET_BLOCK_DELETE_OFF()

    def actOnOptionalStop(self, state):
        if state:
            ACTION.SET_OPTIONAL_STOP_ON()
        else:
            ACTION.SET_OPTIONAL_STOP_OFF()

    def actOnLoadCalibration(self,widget, state=None):
        AUX_PRGM.load_calibration()

    def actOnLoadHalmeter(self,widget, state=None):
        AUX_PRGM.load_halmeter()

    def actOnLoadStatus(self,widget, state=None):
        AUX_PRGM.load_status()

    def actOnLoadHalshow(self,widget, state=None):
        AUX_PRGM.load_halshow()

    def actOnLoadHalscope(self,widget, state=None):
        AUX_PRGM.load_halscope()

    def actOnLoadExtTooledit(self,widget, state=None):
        AUX_PRGM.load_tooledit()

    def actOnLoadClassicladder(self,widget, state=None):
        AUX_PRGM.load_ladder()

    def actOnZoomIn(self,widget, state=None):
        STATUS.emit('view-changed', 'zoom-in')

    def actOnZoomOut(self,widget, state=None):
        STATUS.emit('view-changed', 'zoom-out')

    def actOnViewX(self,widget, state=None):
        STATUS.emit('view-changed', 'x')

    def actOnViewY(self,widget, state=None):
        STATUS.emit('view-changed', 'y')

    def actOnViewY2(self,widget, state=None):
        STATUS.emit('view-changed', 'y2')

    def actOnViewZ(self,widget, state=None):
        STATUS.emit('view-changed', 'z')

    def actOnViewZ2(self,widget, state=None):
        STATUS.emit('view-changed', 'z2')

    def actOnViewp(self,widget, state=None):
        STATUS.emit('view-changed', 'p')

    def actOnViewClear(self,widget, state=None):
        STATUS.emit('view-changed', 'clear')

    def actOnQuit(self,widget, state=None):
        print 'quit'
        STATUS.emit('shutdown')

    def actOnAbout(self,widget, state=None):
        msg = QtWidgets.QMessageBox()

        mess =''
        path = os.path.join(CONFIGDIR, 'README')
        if os.path.exists(path):
            for line in open(path):
                mess += line
            msg.setWindowTitle("README")
        else:
            msg.setWindowTitle("About")
            mess = 'This is a QtVCP based screen for Linuxcnc'
        msg.setText(mess)

        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.show()
        retval = msg.exec_()

    def addHomeActions(self,widget):
        def home(joint):
            print 'home'
            ACTION.SET_MACHINE_HOMING(joint)

        conversion = {"X":0, "Y":1, "Z":2, "A":3, "B":4, "C":5, "U":6, "V":7, "W":8}
        homeAct = QtWidgets.QAction('Home ALL', widget)
        homeAct.triggered.connect(lambda: home(-1))
        widget.addAction(homeAct)
        for i in INFO.AVAILABLE_AXES:
            homeAct = QtWidgets.QAction('Home %s'%i, widget)
            homeAct.triggered.connect(lambda: home(conversion[i]))
            widget.addAction(homeAct)

    def updateRecent(self, widget, filename):
        def loadRecent(w):
            ACTION.OPEN_PROGRAM(w.text())

        # get a list of the current actions
        alist =  widget.actions()

        #build the action
        impAct = QtWidgets.QAction(filename, widget)
        impAct.triggered.connect(lambda:loadRecent(impAct))

        # adding actions is different if it's the first
        # if it's not the first add it before the first
        try:
            widget.insertAction(alist[0],impAct)
        except:
            widget.addAction(impAct)

        # is this a dublicate ?
        for i in alist:
            if i.text() == filename:
                widget.removeAction(i)
                return

        # are we past 5 files? remove the lowest
        # else update cuurrent number
        if self.recentNum  >self.maxRecent:
            widget.removeAction(alist[self.maxRecent])
        else:
            self.recentNum +=1
