#!/usr/bin/env python
from flexbe_core import EventState


class EmptyStateForDistribution(EventState):
    """
    Implements a state that can be used to wait on timed process.

    -- wait_time 	float	Amount of time to wait in seconds.

    <= done					Indicates that the wait time has elapsed.
    """

    def __init__(self):
        super(EmptyStateForDistribution, self).__init__(outcomes=["done"])

    def execute(self, userdata):
        return "done"
