#!/usr/bin/env python

from flexbe_core import EventState, Logger

from random import random

from time import sleep

class SucceedFlagStateForDistribution(EventState):
    '''
    '''

    def __init__(self, sleep_time):
        super(SucceedFlagStateForDistribution, self).__init__(
                outcomes=['done'],
                input_keys=['argument', 'behavior_name'],
                output_keys=['behavior_result'])

        self._sleep_time = sleep_time
        
    # ==================================================================================================
    #
    #   Flexbe Methods
    #
    # ==================================================================================================
    def execute(self, userdata):
        self._behavior_name = userdata.behavior_name
        argument = userdata.argument
        Logger.loginfo(f"Executing behavior {self._behavior_name} with argument {argument}")

        sleep(self._sleep_time)

        Logger.loginfo(f"Behavior {self._behavior_name} succeeded")
        userdata.behavior_result = "succeeded"

        return "done"
