# Motor Control Libraries

Libraries for controlling DC motors, servomotors, and stepper motors with MicroPython on various microcontroller platforms.

Most libraries out there only support basic movements, but here you will find more advance functionalities such as controlling the speed of the servo or moving the motors with the ability to perform other stuff (async-movement).

## Overview

### DCMotor Library

The DCMotor library provides a simple interface to control a DC motor using PWM signals, with support for both synchronous and asynchronous movement.

### Servo Library

The Servo library offers an easy way to control servomotors, with support for both synchronous and asynchronous movement.

### Stepper Library

The Stepper library allows precise control of stepper motors, with support for both synchronous and asynchronous movement.

## Features

### DCMotor Library

- Control motor speed and direction using two PWM pins.
- Fast and slow decay modes.

### Servo Library

- Control servomotor angles with optional speed and asynchronous movement.

### Stepper Library

- Control stepper motors using digital or PWM pins.
- Support for various stepping methods: `SINGLE`, `DOUBLE`, `INTERLEAVE`, `MICROSTEP`.
- Ability to perform continuous movements.

## Installation

Ensure you have MicroPython installed on your microcontroller. Upload the relevant Python files (`dc_motor.py`, `servo.py`, `Stepper.py`) to your microcontroller.

## Usage

### Importing the Libraries

First, import the required libraries:

```python
from DCMotor import DCMotor
from Servo import Servo
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
motor.speed(-50)  # Set speed (range: -100 to 100)
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
servo.move(90)
```

##### Asynchronous Movement

```python
servo.move(90, speed=30, async_mode=True)
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
servo.release()
```

### Stepper Library

#### Initialization

Create a `Stepper` object by specifying the pins for the coils and, optionally, the number of microsteps.

```python
motor = Stepper(ain1=12, ain2=13, bin1=14, bin2=15)
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
motor.step(200, direction=FORWARD, style=SINGLE, rpm=60)
```

- `steps`: Number of steps to perform
- `direction`: Either `FORWARD` or `BACKWARD`
- `style`: One of the stepping methods (`SINGLE`, `DOUBLE`, `INTERLEAVE`, `MICROSTEP`)
- `rpm`: Revolutions per minute

#### Angle-Based Steps

```python
motor.angle(90, direction=FORWARD, style=SINGLE, rpm=60)
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
from DCMotor import DCMotor
import time

motor = DCMotor(pina=0, pinb=1, freq=50, fast=True)
motor.speed(100)  # Set speed
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
