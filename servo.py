from machine import Pin, PWM
import time
import _thread

class Servo:
    def __init__(self, pin, start=0, *, min_angle=0, max_angle=180, freq=50, pulse_min=0.5, pulse_max=2.5):
        """
        Initializes the servo object.

        :param pin: The pin to which the servo is connected.
        :param start: Starting angle of the servo.
        :param min_angle: Minimum angle of the servo in degrees.
        :param max_angle: Maximum angle of the servo in degrees.
        :param freq: PWM frequency.
        :param pulse_min: Minimum pulse width in milliseconds.
        :param pulse_max: Maximum pulse width in milliseconds.
        """
        self._servo = PWM(Pin(pin))
        self._servo.freq(freq)
        self._pulse_min = pulse_min  # Minimum pulse width in milliseconds for 0 degrees
        self._pulse_max = pulse_max  # Maximum pulse width in milliseconds for 180 degrees
        self._freq = freq  # Frequency in Hertz (pulse period in milliseconds)
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._current_angle = start
        self._determine_duty_method()
        self._set_duty(self._angle_to_duty(self._current_angle))
        self._target_angle = self._current_angle
        self._step = 0
        self._step_delay = 0.1
        self._move_thread_running = False
        self._lock = _thread.allocate_lock()

    def _determine_duty_method(self):
        """
        Determines whether to use duty or duty_u16 based on platform support.
        """
        if hasattr(self._servo, "duty_u16"):
            self._set_duty = self._servo.duty_u16
            self._duty_factor = 65535 / (1000 / self._freq)

        else:
            self._set_duty = self._servo.duty
            self._duty_factor = 1023 / (1000 / self._freq)


    def move(self, target_angle, speed=None, async_mode=False):
        """
        Moves the servo to a specific angle.

        :param target_angle: Target angle.
        :param speed: Speed of movement in degrees per second.
        :param async_mode: True for asynchronous movement, False for synchronous movement.
        """
        if not self._min_angle <= target_angle <= self._max_angle:
            raise ValueError(f"Target angle must be between {self._min_angle} and {self._max_angle}.")
    
        self._move_thread_running = False
        with self._lock:
            if speed is None:
                self._set_duty(self._angle_to_duty(target_angle))
                self._target_angle = target_angle
                self._current_angle = target_angle
            else:
                self._step_delay = 1.0 / speed
                self._target_angle = target_angle

                if self._current_angle < self._target_angle:
                    self._step = 1
                else:
                    self._step = -1

                if async_mode:
                    _thread.start_new_thread(self._threaded_move, ())
                else:
                    while self._current_angle != self._target_angle:
                        self._update_angle()
                        time.sleep(self._step_delay)

    def _threaded_move(self):
        """
        Moves the servo in a separate thread to the target angle.
        """
        self._lock.acquire()
        self._move_thread_running = True
        while self._current_angle != self._target_angle and self._move_thread_running:
            self._update_angle()
            time.sleep(self._step_delay)
        self._move_thread_running = False
        self._lock.release()

    def goal_reached(self):
        """
        Checks if the servo has reached its target angle.

        :return: True if the servo has reached its target angle, False otherwise.
        """
        return self._current_angle == self._target_angle
    
    def stop(self):
        """
        Stops the servo movement and cancels the thread.
        """
        self._move_thread_running = False
        self._set_duty(0)

    def release(self):
        """
        Detaches the servo.
        """
        self._servo.deinit()

    def _angle_to_duty(self, angle):
        """
        Converts the angle to duty cycle.

        :param angle: The angle in degrees.
        :return: The duty cycle.
        """
        angle_range = self._max_angle - self._min_angle
        normalized_angle = (angle - self._min_angle) / angle_range
        pulse_width = self._pulse_min + normalized_angle * (self._pulse_max - self._pulse_min)
        duty_cycle = int(pulse_width * self._duty_factor)
        return duty_cycle
    
    def _update_angle(self):
        """
        Moves the servo step by step to the target angle.
        """
        if self._current_angle != self._target_angle:
            self._current_angle += self._step
            duty = self._angle_to_duty(self._current_angle)
            self._set_duty(duty)

    def __del__(self):
        self.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        
