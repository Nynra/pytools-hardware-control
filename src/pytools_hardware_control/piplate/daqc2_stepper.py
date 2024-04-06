import piplates.DAQC2plate as DAQC2


class DAQCStepper:

    def __init__(
        self, address: int, channel: int, steps_per_rev: int = 200, microsteps: int = 16
    ):
        """
        Initialize the DAQC2Stepper controller.

        Parameters
        ----------
        address : int
            The address of the DAQC2 plate.
        steps_per_rev : int
            The number of steps per revolution of the stepper motor.
        microsteps : int
            The number of microsteps per step of the stepper motor.
        """
        if not isinstance(address, int):
            raise TypeError(
                "address must be an integer, not type {}".format(type(address))
            )
        if not isinstance(steps_per_rev, int):
            raise TypeError(
                "steps_per_rev must be an integer, not type {}".format(
                    type(steps_per_rev)
                )
            )
        if not isinstance(microsteps, int):
            raise TypeError(
                "microsteps must be an integer, not type {}".format(type(microsteps))
            )

        self._address = address
        self._steps_per_rev = steps_per_rev
        self._microsteps = microsteps
        self._directions = [1, 1]

    def enable(self) -> ...:
        """Enable Motor Control on the DAQC2 plate."""
        DAQC2.motorENABLE(self._address)

    def disable(self) -> ...:
        """Disable Motor Control on the DAQC2 plate."""
        DAQC2.motorDISABLE(self._address)

    def turn_off_motor(self, channel: int) -> ...:
        """Stop and remove power from the specified motor."""
        self._verify_motor(channel)
        DAQC2.motorOFF(self._address, channel)

    def stop_motor(self, channel: int) -> ...:
        """Stop the specified motor (does not remove power)."""
        self._verify_motor(channel)
        DAQC2.motorSTOP(self._address, self._channel)

    def move(self, steps: int, channel: int) -> ...:
        """Move the motor a specified number of steps."""
        if not isinstance(steps, int):
            raise TypeError(
                "steps must be an integer, not type {}".format(type(steps))
            )
        self._verify_motor(channel)
        DAQC2.stepperMOVE(self._address, self._channel, steps)

    def jog(self, channel: int) -> ...:
        """Jog the motor in the specified direction.
        
        .. warning::
        
            The motor will continue until the motor is stopped or the power 
            is removed.
            
        """
        self._verify_motor(channel)
        DAQC2.stepperJOG(
            self._address,
            self._channel,
            self._directions[channel],
        )

    def set_direction(self, direction: int, channel: int) -> ...:
        """Set the direction of the motor."""
        if not isinstance(direction, int):
            raise TypeError(
                "direction must be an integer, not type {}".format(type(direction))
            )
        if direction not in [-1, 1]:
            raise ValueError("direction must be -1 or 1, not {}".format(direction))
        self._verify_motor(channel)
        self._directions[channel] = direction
        DAQC2.motorDIR(self._address, channel, "ccw" if direction == -1 else "cw")

    def get_direction(self, channel: int) -> int:
        """Get the direction of the motor."""
        if not isinstance(channel, int):
            raise TypeError(
                "channel must be an integer, not type {}".format(type(channel))
            )
        self._verify_motor(channel)
        return self._directions[channel]

    def set_speed(self, speed: int, channel: int) -> ...:
        """Set the speed of the motor."""
        if not isinstance(speed, int):
            raise TypeError(
                "speed must be an integer, not type {}".format(type(speed))
            )
        self._verify_motor(channel)
        DAQC2.stepperRATE(self._address, channel, speed)

    def _verify_motor(self, channel: int) -> ...:
        """Verify the motor is connected."""
        if not isinstance(channel, int):
            raise TypeError(
                "channel must be an integer, not type {}".format(type(channel))
            )
        if channel not in [1, 2]:
            raise ValueError("Invalid channel: {}".format(channel))
