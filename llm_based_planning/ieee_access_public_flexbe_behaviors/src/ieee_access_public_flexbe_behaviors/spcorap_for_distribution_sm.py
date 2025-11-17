#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################
#               WARNING: Generated code!                  #
#              **************************                 #
# Manual changes may get lost if file is generated again. #
# Only code inside the [MANUAL] tags will be kept.        #
###########################################################

from flexbe_core import Behavior, Autonomy, OperatableStateMachine, ConcurrencyContainer, PriorityContainer, Logger
from ieee_access_public_flexbe_states.empty_state_for_distribution import EmptyStateForDistribution
from ieee_access_public_flexbe_states.fail_flag_state_for_distribution import FailFlagStateForDistribution
from ieee_access_public_flexbe_states.spcorap_planner_for_distribution import SpCoRAPPlannerForDistribution
from ieee_access_public_flexbe_states.succeed_flag_state_for_distribution import SucceedFlagStateForDistribution
# Additional imports can be added inside the following tags
# [MANUAL_IMPORT]

# [/MANUAL_IMPORT]


'''
Created on Mon Nov 17 2025
@author: Shoichi Hasegawa
'''
class spcorap_for_distributionSM(Behavior):
	'''
	This behavior is spcorap behavior for distribution.
	'''


	def __init__(self):
		super(spcorap_for_distributionSM, self).__init__()
		self.name = 'spcorap_for_distribution'

		# parameters of this behavior

		# references to used behaviors

		# Additional initialization code can be added inside the following tags
		# [MANUAL_INIT]
		
		# [/MANUAL_INIT]

		# Behavior comments:



	def create(self):
		# x:133 y:440, x:33 y:440
		_state_machine = OperatableStateMachine(outcomes=['finished', 'failed'])
		_state_machine.userdata.instruction = "Bring me an apple."
		_state_machine.userdata.behavior_result = None

		# Additional creation code can be added inside the following tags
		# [MANUAL_CREATE]
		
		# [/MANUAL_CREATE]


		with _state_machine:
			# x:153 y:274
			OperatableStateMachine.add('planner',
										SpCoRAPPlannerForDistribution(model_name="o3-2025-04-16", method="spcorap"),
										transitions={'navigation': 'navigation', 'object_detection': 'object detection', 'pick': 'pick', 'place': 'place', 'finished': 'finished', 'failed': 'failed'},
										autonomy={'navigation': Autonomy.Off, 'object_detection': Autonomy.Off, 'pick': Autonomy.Off, 'place': Autonomy.Off, 'finished': Autonomy.Off, 'failed': Autonomy.Off},
										remapping={'instruction': 'instruction', 'behavior_result': 'behavior_result', 'argument': 'argument', 'behavior_name': 'behavior_name', 'save_data_path': 'save_data_path'})

			# x:1003 y:224
			OperatableStateMachine.add('empty_2_2',
										EmptyStateForDistribution(),
										transitions={'done': 'empty_2'},
										autonomy={'done': Autonomy.Off})

			# x:253 y:524
			OperatableStateMachine.add('empty_3',
										EmptyStateForDistribution(),
										transitions={'done': 'planner'},
										autonomy={'done': Autonomy.Off})

			# x:753 y:317
			OperatableStateMachine.add('fail',
										FailFlagStateForDistribution(sleep_time=1),
										transitions={'done': 'empty_2_2'},
										autonomy={'done': Autonomy.Off},
										remapping={'argument': 'argument', 'behavior_name': 'behavior_name', 'behavior_result': 'behavior_result'})

			# x:453 y:124
			OperatableStateMachine.add('navigation',
										EmptyStateForDistribution(),
										transitions={'done': 'success'},
										autonomy={'done': Autonomy.Off})

			# x:453 y:224
			OperatableStateMachine.add('object detection',
										EmptyStateForDistribution(),
										transitions={'done': 'success'},
										autonomy={'done': Autonomy.Off})

			# x:453 y:324
			OperatableStateMachine.add('pick',
										EmptyStateForDistribution(),
										transitions={'done': 'success'},
										autonomy={'done': Autonomy.Off})

			# x:453 y:424
			OperatableStateMachine.add('place',
										EmptyStateForDistribution(),
										transitions={'done': 'success'},
										autonomy={'done': Autonomy.Off})

			# x:753 y:167
			OperatableStateMachine.add('success',
										SucceedFlagStateForDistribution(sleep_time=1),
										transitions={'done': 'empty_2_2'},
										autonomy={'done': Autonomy.Off},
										remapping={'argument': 'argument', 'behavior_name': 'behavior_name', 'behavior_result': 'behavior_result'})

			# x:1003 y:524
			OperatableStateMachine.add('empty_2',
										EmptyStateForDistribution(),
										transitions={'done': 'empty_3'},
										autonomy={'done': Autonomy.Off})


		return _state_machine


	# Private functions can be added inside the following tags
	# [MANUAL_FUNC]
	
	# [/MANUAL_FUNC]
