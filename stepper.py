"""
Based on: https://github.com/adafruit/Adafruit_CircuitPython_Motor/blob/main/adafruit_motor/stepper.py
* Author(s): Tony DiCola, Scott Shawcroft, Christopher Nadler
"""

import math
from micropython import const
from machine import Pin, PWM
import time
import _thread

# Constants that specify the direction and style of steps.
FORWARD = const(1)    # Step forward
BACKWARD = const(2)   # Step backward

SINGLE = const(1)     # Step so that each step only activates a single coil
DOUBLE = const(2)     # Step so that each step activates two coils to produce more torque
INTERLEAVE = const(3) # Step half a step to alternate between single coil and double coil steps
MICROSTEP = const(4)  # Step a fraction of a step by partially activating two neighboring coils. Step size is determined by `microsteps` constructor argument

# Coil activation sequences for different step styles.
_SINGLE_STEPS = bytes([0b0010, 0b0100, 0b0001, 0b1000])
_DOUBLE_STEPS = bytes([0b1010, 0b0110, 0b0101, 0b1001])
_INTERLEAVE_STEPS = bytes([0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001, 0b1001, 0b1000])

class Stepper:
    """A class to control a bipolar stepper motor or four coil unipolar motor. 
    The use of microstepping requires pins that can output PWM. 
    For non-microstepping, you can set `microsteps` to None and use digital out pins."""

    def __init__(self, ain1: int, ain2: int, bin1: int, bin2: int, *, microsteps: int = None, steps_per_rev: int = 200) -> None:
        """Initialize the stepper motor.

        :param ain1: Pin number for coil A1
        :param ain2: Pin number for coil A2
        :param bin1: Pin number for coil B1
        :param bin2: Pin number for coil B2
        :param microsteps: Number of microsteps (optional)
        :param steps_per_rev: Number of steps per revolution
        """
        self.steps_per_rev = steps_per_rev
        self._stop_requested = False

        if microsteps is None:
            # Digital IO Pins
            self._steps = None
            self._coil = (Pin(ain1, Pin.OUT), Pin(ain2, Pin.OUT), Pin(bin1, Pin.OUT), Pin(bin2, Pin.OUT))
        else:
            # PWM Pins
            self._coil = (PWM(Pin(ain2)), PWM(Pin(bin1)), PWM(Pin(ain1)), PWM(Pin(bin2)))
            for i in range(4):
                if self._coil[i].freq() < 1500:
                    try:
                        self._coil[i].freq(2000)
                    except AttributeError as err:
                        raise ValueError(
                            "PWMOut outputs must either be set to at least "
                            "1500 Hz or allow variable frequency."
                        ) from err
            if microsteps < 2:
                raise ValueError("Microsteps must be at least 2")
            if microsteps % 2 == 1:
                raise ValueError("Microsteps must be even")
            self._curve = [
                int(round(1023 * math.sin(math.pi / (2 * microsteps) * i)))
                for i in range(microsteps + 1)
            ]

            # Determine which duty method to use
            if hasattr(self._coil[0], 'duty_u16'):
                self._set_duty = lambda coil, value: coil.duty_u16(value)
                self._duty_max = 65535
            else:
                self._set_duty = lambda coil, value: coil.duty(value)
                self._duty_max = 1023

        self._current_microstep = 0
        self._microsteps = microsteps
        self._update_coils()

    def onestep(self, *, direction: int = FORWARD, style: int = SINGLE) -> int:
        """Perform one step of a particular style. 

        :param direction: Either `FORWARD` or `BACKWARD`
        :param style: `SINGLE`, `DOUBLE`, `INTERLEAVE`, or `MICROSTEP`
        :return: The current microstep
        """
        if self._microsteps is None:
            step_size = 1
            if style == SINGLE:
                self._steps = _SINGLE_STEPS
            elif style == DOUBLE:
                self._steps = _DOUBLE_STEPS
            elif style == INTERLEAVE:
                self._steps = _INTERLEAVE_STEPS
            else:
                raise ValueError("Unsupported step style.")
        else:
            step_size = 0
            if style == MICROSTEP:
                step_size = 1
            else:
                half_step = self._microsteps // 2
                full_step = self._microsteps
                additional_microsteps = self._current_microstep % half_step
                if additional_microsteps != 0:
                    if direction == FORWARD:
                        self._current_microstep += half_step - additional_microsteps
                    else:
                        self._current_microstep -= additional_microsteps
                    step_size = 0
                elif style == INTERLEAVE:
                    step_size = half_step

                current_interleave = self._current_microstep // half_step
                if (style == SINGLE and current_interleave % 2 == 1) or (
                    style == DOUBLE and current_interleave % 2 == 0
                ):
                    step_size = half_step
                elif style in (SINGLE, DOUBLE):
                    step_size = full_step

        if direction == FORWARD:
            self._current_microstep += step_size
        else:
            self._current_microstep -= step_size

        self._update_coils(microstepping=style == MICROSTEP)
        return self._current_microstep

    def step(self, steps, direction=FORWARD, style=SINGLE, *, rpm=1, async_mode=False):
        """Performs a specified number of steps.

        :param steps: Number of steps to perform
        :param direction: Either `FORWARD` or `BACKWARD`
        :param style: `SINGLE`, `DOUBLE`, `INTERLEAVE`, or `MICROSTEP`
        :param rpm: Speed in revolutions per second
        :param async_mode: If True, the function will run in a separate thread
        """
        delay = 1 / (rpm * self.steps_per_rev)

        def _step_worker():
            for _ in range(steps):
                if self._stop_requested:
                    break
                self.onestep(direction=direction, style=style)
                time.sleep(delay)
            self._stop_requested = False

        if async_mode:
            _thread.start_new_thread(_step_worker, ())
        else:
            _step_worker()

    def angle(self, angle, direction=FORWARD, style=SINGLE, *, rpm=1, async_mode=False):
        """Performs a specified number of steps corresponding to an angle.

        :param angle: Angle in degrees
        :param direction: Either `FORWARD` or `BACKWARD`
        :param style: `SINGLE`, `DOUBLE`, `INTERLEAVE`, or `MICROSTEP`
        :param rpm: Speed in revolutions per second
        :param async_mode: If True, the function will run in a separate thread
        """
        steps = int(self.steps_per_rev * angle / 360)
        self.step(steps, direction, style, rpm=rpm, async_mode=async_mode)

    def continuous(self, direction=FORWARD, style=SINGLE, *, rpm=1, async_mode=False):
        """Performs continuous steps.

        :param direction: Either `FORWARD` or `BACKWARD`
        :param style: `SINGLE`, `DOUBLE`, `INTERLEAVE`, or `MICROSTEP`
        :param rpm: Speed in revolutions per second
        :param async_mode: If True, the function will run in a separate thread
        """
        delay = 1 / (rpm * self.steps_per_rev)

        def _continuous_worker():
            while not self._stop_requested:
                self.onestep(direction=direction, style=style)
                time.sleep(delay)
            self._stop_requested = False

        if async_mode:
            _thread.start_new_thread(_continuous_worker, ())
        else:
            _continuous_worker()

    def stop(self):
        """Stops any ongoing movement."""
        self._stop_requested = True
        
    def release(self) -> None:
        """Releases all the coils so the motor can free spin and won't use any power."""
        for coil in self._coil:
            if self._microsteps is None:
                coil.value(0)
            else:
                self._set_duty(coil, 0)
                
    def _update_coils(self, *, microstepping: bool = False) -> None:
        """Update the coil energizing based on the current step."""
        if self._microsteps is None:
            # Digital IO Pins
            steps = 0b0000 if self._steps is None else self._steps[self._current_microstep % len(self._steps)]
            for i, coil in enumerate(self._coil):
                coil.value((steps >> i) & 0x01)
        else:
            # PWM Pins
            duty_cycles = [0, 0, 0, 0]
            trailing_coil = (self._current_microstep // self._microsteps) % 4
            leading_coil = (trailing_coil + 1) % 4
            microstep = self._current_microstep % self._microsteps
            duty_cycles[leading_coil] = self._curve[microstep]
            duty_cycles[trailing_coil] = self._curve[self._microsteps - microstep]

            if not microstepping and (
                duty_cycles[leading_coil] == duty_cycles[trailing_coil]
                and duty_cycles[leading_coil] > 0
            ):
                duty_cycles[leading_coil] = self._duty_max
                duty_cycles[trailing_coil] = self._duty_max

            for i in range(4):
                self._set_duty(self._coil[i], duty_cycles[i])

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __del__(self):
        self.release()
