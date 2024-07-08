# Motor Control Libraries

This repository provides libraries for controlling DC motors, servomotors, and stepper motors with MicroPython on various microcontroller platforms.

## Overview

### DCMotor Library

The DCMotor library provides a simple interface to control a DC motor using PWM (Pulse Width Modulation) signals. It supports both fast and slow decay modes and allows setting the motor speed and direction.

### Servo Library

The Servo library offers an easy way to control servomotors, with support for various microcontroller platforms and functionality for both synchronous and asynchronous movement.

### Stepper Library

The Stepper library allows precise control of stepper motors. It supports both digital and PWM pins, various stepping methods including microstepping, and offers adjustable speed and torque.

## Features

### DCMotor Library

- Control motor speed and direction using two PWM pins.
- Supports both 10-bit and 16-bit PWM resolution.
- Fast and slow decay modes.

### Servo Library

- Control servomotor angles with optional speed and asynchronous movement.
- Supports both 10-bit and 16-bit PWM resolution.

### Stepper Library

- Control stepper motors using digital or PWM pins.
- Support for various stepping methods: `SINGLE`, `DOUBLE`, `INTERLEAVE`, `MICROSTEP`.
- Adjustable speed and torque.
- Ability to perform continuous movements.
- Supports both `duty` and `duty_u16` methods for PWM.

## Installation

Ensure you have MicroPython installed on your microcontroller. Upload the relevant Python files (`dc_motor.py`, `servo.py`, `Stepper.py`) to your microcontroller.

## Usage

### Importing the Libraries

First, import the required libraries:

```python
from machine import Pin, PWM
from dc_motor import DCMotor  # Assuming you saved the class in a file named dc_motor.py
from servo import Servo      # Assuming you saved the class in a file named servo.py
from Stepper import Stepper
```

### DCMotor Library

#### Initialization

Create an instance of the `DCMotor` class by specifying the pins for speed and direction control, the PWM frequency, and the decay mode.

```python
# Initialize the motor with fast decay mode
motor = DCMotor(pina=0, pinb=1, freq=50, fast=True)
```

#### Controlling the Motor

Set the motor speed and direction:

```python
motor.speed(512)  # Set speed (range: -1023 to 1023)
```

Stop the motor:

```python
motor.stop()
```

### Servo Library

#### Initialization

Create a Servo object by specifying the pin to which the servomotor is connected. Optional parameters include the start angle, minimum and maximum angles, PWM frequency, and minimum and maximum pulse widths.

```python
servo = Servo(pin=2, start=0)
```

#### Moving the Servomotor

Use the `move` method to move the servomotor to a specific angle. Optionally, you can specify the movement speed and asynchronous mode.

##### Synchronous Movement

```python
servo.move(target_angle=90)
```

##### Asynchronous Movement

```python
servo.move(target_angle=90, speed=30, async_mode=True)
```

#### Checking if the Target is Reached

Use the `goal_reached` method to check if the servomotor has reached the target angle.

```python
if servo.goal_reached():
    print("The servo has reached the target.")
```

#### Stopping the Servomotor

Use the `stop` method to stop the servomotor's movement.

```python
servo.stop()
```

#### Detaching the Servomotor

Use the `detach` method to detach the servomotor.

```python
servo.detach()
```

### Stepper Library

#### Initialization

Create a `Stepper` object by specifying the pins for the coils and, optionally, the number of microsteps.

```python
motor = Stepper(ain1=12, ain2=13, bin1=14, bin2=15, microsteps=16)
```

- `ain1`, `ain2`, `bin1`, `bin2`: Pin numbers for coil connections
- `microsteps`: Number of microsteps (optional, default is None for digital outputs)

#### Single Step

```python
motor.onestep(direction=FORWARD, style=SINGLE)
```

- `direction`: Either `FORWARD` or `BACKWARD`
- `style`: One of the stepping methods (`SINGLE`, `DOUBLE`, `INTERLEAVE`, `MICROSTEP`)

#### Performing Steps

```python
motor.step(steps=200, direction=FORWARD, style=SINGLE, rpm=60)
```

- `steps`: Number of steps to perform
- `direction`: Either `FORWARD` or `BACKWARD`
- `style`: One of the stepping methods (`SINGLE`, `DOUBLE`, `INTERLEAVE`, `MICROSTEP`)
- `rpm`: Revolutions per minute

#### Angle-Based Steps

```python
motor.angle(angle=90, direction=FORWARD, style=SINGLE, rpm=60)
```

- `angle`: Angle in degrees

#### Continuous Movement

```python
motor.continuous(direction=FORWARD, style=SINGLE, rpm=60)
```

- `direction`: Either `FORWARD` or `BACKWARD`
- `style`: One of the stepping methods (`SINGLE`, `DOUBLE`, `INTERLEAVE`, `MICROSTEP`)
- `rpm`: Revolutions per minute

#### Stop Movement

```python
motor.stop()
```

#### Release Coils

```python
motor.release()
```

## Examples

### DCMotor Example

Here is a complete example of using the DCMotor library:

```python
from machine import Pin, PWM
from dc_motor import DCMotor
import time

motor = DCMotor(pina=0, pinb=1, freq=50, fast=True)
motor.speed(512)  # Set speed
time.sleep(5)  # Run for 5 seconds
motor.stop()  # Stop the motor
```

### Servo Example

Here is a complete example of using the Servo library:

```python
from servo import Servo
import time

servo = Servo(pin=2, start=0)
servo.move(90, speed=30, async_mode=True)  # 30 degrees per second
time.sleep(5)  # Wait for 5 seconds to let the servo move
servo.stop()
```

### Stepper Example

Here is a complete example of using the Stepper library:

```python
from Stepper import Stepper
import time

motor = Stepper(ain1=12, ain2=13, bin1=14, bin2=15, microsteps=16)
motor.step(steps=200, direction=FORWARD, style=SINGLE, rpm=60)  # Move 200 steps
time.sleep(5)  # Wait for 5 seconds
motor.stop()  # Stop the motor
```

## Supported Platforms

These libraries support platforms that can use `machine.Pin`, `machine.PWM`, and `_thread` modules in MicroPython.

## License

These projects are licensed under the MIT License - see the LICENSE file for details.