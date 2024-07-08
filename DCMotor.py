from machine import Pin, PWM

class DCMotor:
    def __init__(self, pina:int, pinb:int, *, freq:int=50, fast:bool=True):
        """
        Initializes the DC motor with specified pins, PWM frequency, and decay mode.

        :param pina: The first PWM pin for speed control.
        :param pinb: The second PWM pin for direction control.
        :param freq: The PWM frequency (default: 50 Hz).
        :param fast: Boolean indicating the decay mode (True for fast decay, False for slow decay).
        """
        self._pwm_a = PWM(Pin(pina), duty=0)
        self._pwm_b = PWM(Pin(pinb), duty=0)
        self._pwm_a.freq(freq)
        self._pwm_b.freq(freq)
        self._fast_decay = fast
        self._speed = 0  # Default speed in percentage, initially stopped

        # Determine the appropriate function handle based on PWM resolution
        if hasattr(self._pwm_a, 'duty_u16') and hasattr(self._pwm_b, 'duty_u16'):
            self._set_pwm_duty = self._set_duty_16
        else:
            self._set_pwm_duty = self._set_duty_10

    @property
    def speed(self):
        """Gets the current speed of the motor."""
        return self._speed

    @speed.setter
    def speed(self, value:int):
        """Sets the speed of the motor and updates the PWM duty cycle."""
        if -100 <= value <= 100:
            self._speed = value
            self._set_pwm_duty()
        else:
            raise ValueError("Speed percent must be between -100 and 100")

    @property
    def decay(self):
        """Gets the current decay mode of the motor."""
        return self._fast_decay

    @decay.setter
    def decay(self, value:bool):
        """Sets the decay mode of the motor and updates the PWM duty cycle."""
        self._fast_decay = value
        self._set_pwm_duty()

    def throttle(self, speed, fast=None):
        """
        Moves the motor with the specified speed and decay mode.

        :param speed: Speed in percentage (-100 to 100).
                      Negative values for reverse, positive values for forward.
        :param fast: Boolean indicating the decay mode (True for fast decay, False for slow decay).
        :raises ValueError: If speed is not between -100 and 100.
        """
        if speed is not None:
            self.speed = speed
        
        if fast is not None:
            self.decay = fast

        self._set_pwm_duty()

    def _set_duty_16(self):
        """Sets the PWM duty cycle for 16-bit resolution."""
        duty_cycle_u16 = int(abs(self._speed) * 65535 / 100)
        if self._speed >= 0:
            if self._fast_decay:
                self._pwm_a.duty_u16(duty_cycle_u16)
                self._pwm_b.duty_u16(0)
            else:
                self._pwm_b.duty_u16(65535 - duty_cycle_u16)
                self._pwm_a.duty_u16(65535)
        else:
            if self._fast_decay:
                self._pwm_a.duty_u16(0)
                self._pwm_b.duty_u16(duty_cycle_u16)
            else:
                self._pwm_b.duty_u16(65535)
                self._pwm_a.duty_u16(65535 - duty_cycle_u16)

    def _set_duty_10(self):
        """Sets the PWM duty cycle for 10-bit resolution."""
        duty_cycle = int(abs(self._speed) * 1023 / 100)
        if self._speed >= 0:
            if self._fast_decay:
                self._pwm_a.duty(duty_cycle)
                self._pwm_b.duty(0)
            else:
                self._pwm_b.duty(1023 - duty_cycle)
                self._pwm_a.duty(1023)
        else:
            if self._fast_decay:
                self._pwm_a.duty(0)
                self._pwm_b.duty(duty_cycle)
            else:
                self._pwm_b.duty(1023)
                self._pwm_a.duty(1023 - duty_cycle)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Releases the PWM resources."""
        self._pwm_a.deinit()
        self._pwm_b.deinit()
