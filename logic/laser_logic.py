#-*- coding: utf-8 -*-
"""
Laser management.

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

from qtpy import QtCore
import numpy as np
import time

from logic.generic_logic import GenericLogic
from interface.simple_laser_interface import ControlMode, ShutterState, LaserState

class LaserLogic(GenericLogic):
    """ Logic module agreggating multiple hardware switches.
    """
    _modclass = 'laser'
    _modtype = 'logic'
    _in = {'laser': 'SimpleLaserInterface'}
    _out = {'laserlogic': 'LaserLogic'}

    sigUpdate = QtCore.Signal()

    def on_activate(self, e):
        """ Prepare logic module for work.

          @param object e: Fysom state change notification
        """
        self._laser = self.get_in_connector('laser')
        self.stopRequest = False
        self.bufferLength = 100
        self.data = {}
        # waiting time between queries im milliseconds
        self.queryInterval = 100

        # delay timer for querying laser
        self.queryTimer = QtCore.QTimer()
        self.queryTimer.setInterval(self.queryInterval)
        self.queryTimer.setSingleShot(True)
        self.queryTimer.timeout.connect(self.check_laser_loop, QtCore.Qt.QueuedConnection)

        # get laser capabilities
        self.laser_shutter = self._laser.get_shutter_state()
        self.laser_power_range = self._laser.get_power_range()
        self.laser_extra = self._laser.get_extra_info()
        self.laser_state = self._laser.get_laser_state()
        self.laser_can_turn_on = self.laser_state.value <= LaserState.ON.value
        self.laser_can_power = ControlMode.POWER in self._laser.allowed_control_modes()
        self.laser_can_current = ControlMode.CURRENT in self._laser.allowed_control_modes()
        if ControlMode.MIXED in self._laser.allowed_control_modes():
            self.laser_can_power = True
            self.laser_can_current = True

        self.has_shutter = self._laser.get_shutter_state() != ShutterState.NOSHUTTER
        self.init_data_logging()
        #QtCore.QTimer.singleShot(100, self.start_query_loop)
        self.start_query_loop()

    def on_deactivate(self, e):
        """ Deactivate modeule.

          @param object e: Fysom state change notification
        """
        self.stop_query_loop()

    @QtCore.Slot()
    def check_laser_loop(self):
        """ """
        if self.stopRequest:
            self.stop()
            self.stopRequest = False
            return

        self.laser_state = self._laser.get_laser_state()
        self.laser_shutter = self._laser.get_shutter_state()
        self.laser_power = self._laser.get_power()
        self.laser_current = self._laser.get_current()
        self.laser_temps = self._laser.get_temperatures()

        for k in self.data:
            self.data[k] = np.roll(self.data[k], -1)

        self.data['power'][-1] = self.laser_power
        self.data['current'][-1] = self.laser_current
        self.data['time'][-1] = time.time()

        for k,v in self.laser_temps.items():
            self.data[k][-1] = v

        self.queryTimer.start(self.queryInterval)
        self.sigUpdate.emit()

    @QtCore.Slot()
    def start_query_loop(self):
        """ start the loop """
        self.run()
        self.queryTimer.start(self.queryInterval)

    @QtCore.Slot()
    def stop_query_loop(self):
        """ stop loop """
        self.stopRequest = True
        for i in range(10):
            if not self.stopRequest:
                return
            QtCore.QCoreApplication.processEvents()
            time.sleep(self.queryInterval/1000)

    def init_data_logging(self):
        """ """
        self.data['current'] = np.zeros(self.bufferLength)
        self.data['power'] = np.zeros(self.bufferLength)
        self.data['time'] = np.ones(self.bufferLength) * time.time()
        temps = self._laser.get_temperatures()
        for name in temps:
            self.data[name] = np.zeros(self.bufferLength)

    @QtCore.Slot(ControlMode)
    def set_control_mode(self, mode):
        """ """
        if mode in self._laser.allowed_control_modes():
            if mode == ControlMode.POWER:
                self.laser_power = self._laser.get_power()
                self._laser.set_power(self.laser_power)
                self._laser.set_control_mode(mode)
            elif mode == ControlMode.CURRENT:
                self.laser_current = self._laser.get_current()
                self._laser.set_current(self.laser_current)
                self._laser.set_control_mode(mode)

    @QtCore.Slot(float)
    def set_laser_state(self, state):
        if state and self.laser_state == LaserState.OFF:
            self._laser.on()
        if not state and self.laser_state == LaserState.ON:
            self._laser.off()

    @QtCore.Slot(bool)
    def set_shutter_state(self, state):
        if state and self.laser_shutter == ShutterState.CLOSED:
            self._laser.set_shutter_state(ShutterState.OPEN)
        if not state and self.laser_shutter == ShutterState.OPEN:
            self._laser.set_shutter_state(ShutterState.CLOSED)

    @QtCore.Slot(float)
    def set_power(self, power):
        self._laser.set_power(power)

    @QtCore.Slot(float)
    def set_current(self, current):
        self._laser.set_current(current)