""" [unittest]-compatible test case for testing trial state transition 
    sequences for the `delay_out_center_task`, via the ROS2 graph.

[unittest]: https://docs.pytest.org
"""

# Copyright 2022 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Import unittest.
import unittest

# Local imports.
from delay_out_center_task import Environment
from delay_out_center_task import Model
from delay_out_center_task import Machine


# Define test case.
class TestCase(unittest.TestCase):
    """ Test case for testing valid sequences of trial states. """
    
    def setUp(self):
        """ Initialize the environment, model, and state machine. """
        
        # Override the `timeout` trigger function, to disable automatic state 
        # transitions in this local context. This is important for testing.
        Model.timeout = lambda s, *a, **k: None
        
        # Initialize the task environment.
        self.environment = Environment()
        
        # Initialize the behavioral model for the state machine.
        self.model = Model(environment=self.environment)
        
        # Initialize the state machine.
        self.machine = Machine(model=self.model)
        
    def tearDown(self):
        """ Terminate. """
        pass
        
    def trigger(self, event, expected_state=''):
        """ Trigger a state transition. """
        result = self.model.trigger(event)
        if expected_state: assert(self.state == expected_state)
        return result
        
    @property
    def state(self):
        """ Current state of the state machine. """
        return self.model.state
    
    def _trigger_end_block(self):
        """ """
        
        # Reset to inactive state.
        # Verify that the cursor is the only object in the environment.
        self.trigger('end_block', expected_state='inactive')
        assert(list(self.environment.objects) == ['cursor'])
        
    def _trigger_start_block(self):
        """ """
        
        # Start a block of trials.
        # Verify that the targets have been loaded.
        self.trigger('start_block', expected_state='intertrial')
        assert(len(self.model.targets) > 0)
    
    def _trigger_intertrial_timeout(self):
        """ """
        
        # Start waiting for Target A to be engaged.
        # Verify that the target index is updated.
        # Verify that the target is placed in the home position.
        # Verify that a target has been added to the environment.
        target_index = self.model.target_index
        self.trigger('timeout', expected_state='move_a')
        assert(self.model.target_index != target_index)
        assert(self.environment.get_position('target') == (0.0, 0.0, 0.0))
        assert('target' in self.environment.objects)
        
    def _trigger_move_a_target_engaged(self):
        """ """
        
        # Indicate that Target A is engaged, and start waiting for the hold 
        # interval to expire.
        self.trigger('target_engaged', expected_state='hold_a')
        
    def _trigger_hold_a_timeout(self):
        """ """
        
        # Transition to the delay state and start waiting.
        # Verify that a cue target has added to the environment.
        self.trigger('timeout', expected_state='delay_a')
        assert('cue' in self.environment.objects)
        
    def _trigger_delay_a_timeout(self):
        """ """
        
        # Transition to the move state and start waiting for Target B to be 
        # engaged.
        # Verify that the target has moved to the cue position.
        # Verify that the cue has been removed from the environment.
        target_position = self.environment.get_position('target')
        cue_position = self.environment.get_position('cue')
        self.trigger('timeout', expected_state='move_b')
        assert(self.environment.get_position('target') != target_position)
        assert(self.environment.get_position('target') == cue_position)
        assert('cue' not in self.environment.objects)
        
    def _trigger_move_b_target_engaged(self):
        """ """
        
        # Indicate that Target B is engaged, and start waiting for the hold 
        # interval to expire.
        self.trigger('target_engaged', expected_state='hold_b')
        
    def _trigger_hold_b_timeout(self):
        """ """
        
        # Transition to the move state and start waiting for Target C to be 
        # engaged.
        # Verify that the target has moved to the home position.
        target_position = self.environment.get_position('target')
        home_position = (0.0, 0.0, 0.0)
        self.trigger('timeout', expected_state='move_c')
        assert(self.environment.get_position('target') != target_position)
        assert(self.environment.get_position('target') == home_position)
        
    def _trigger_move_c_target_engaged(self):
        """ """
        
        # Indicate that Target C is engaged, and start waiting for the hold 
        # interval to expire.
        self.trigger('target_engaged', expected_state='hold_c')
        
    def _trigger_failure_timeout(self):
        """ """
        
        # Teardown.
        # Verify that the cursor is the only object in the environment.        
        self.trigger('timeout', expected_state='intertrial')
        assert(list(self.environment.objects) == ['cursor'])
    
    def test_success(self):
        """ Verify a successful trial sequence. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        self._trigger_move_a_target_engaged()
        self._trigger_hold_a_timeout()
        self._trigger_delay_a_timeout()
        self._trigger_move_b_target_engaged()
        self._trigger_hold_b_timeout()
        self._trigger_move_c_target_engaged()
        
        # Success. Hold C timeout.
        self.trigger('timeout', expected_state='success')
        
        # Teardown.
        # Verify that the cursor is the only object in the environment.        
        self.trigger('timeout', expected_state='intertrial')
        assert(list(self.environment.objects) == ['cursor'])
    
    def test_hold_c_failure(self):
        """ Verify a trial sequence that results in a final hold failure. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        self._trigger_move_a_target_engaged()
        self._trigger_hold_a_timeout()
        self._trigger_delay_a_timeout()
        self._trigger_move_b_target_engaged()
        self._trigger_hold_b_timeout()
        self._trigger_move_c_target_engaged()
        
        # Failure due to target disengagement.
        self.trigger('target_disengaged', expected_state='failure')
        
        # Teardown.
        self._trigger_failure_timeout()
        
    def test_move_c_failure(self):
        """ Verify a trial sequence that results in a final move failure. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        self._trigger_move_a_target_engaged()
        self._trigger_hold_a_timeout()
        self._trigger_delay_a_timeout()
        self._trigger_move_b_target_engaged()
        self._trigger_hold_b_timeout()
        
        # Failure to engage target before timeout.
        self.trigger('timeout', expected_state='failure')
        
        # Teardown.
        self._trigger_failure_timeout()
    
    def test_hold_b_failure(self):
        """ Verify a trial sequence that results in a hold B failure. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        self._trigger_move_a_target_engaged()
        self._trigger_hold_a_timeout()
        self._trigger_delay_a_timeout()
        self._trigger_move_b_target_engaged()
        
        # Failure due to target disengagement during `hold_b`.
        self.trigger('target_disengaged', expected_state='failure')
        
        # Teardown.
        self._trigger_failure_timeout()
    
    def test_move_b_failure(self):
        """ Verify a trial sequence that results in a hold B failure. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        self._trigger_move_a_target_engaged()
        self._trigger_hold_a_timeout()
        self._trigger_delay_a_timeout()
        
        # Failure due to target disengagement during `hold_b`.
        self.trigger('timeout', expected_state='failure')
        
        # Teardown.
        self._trigger_failure_timeout()
    
    def test_delay_a_failure(self):
        """ Verify a trial sequence that results in a hold B failure. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        self._trigger_move_a_target_engaged()
        self._trigger_hold_a_timeout()
        
        # Failure due to target disengagement during `hold_b`.
        self.trigger('target_disengaged', expected_state='failure')
        
        # Teardown.
        self._trigger_failure_timeout()
    
    def test_hold_a_failure(self):
        """ Verify a trial sequence that results in a hold B failure. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        self._trigger_move_a_target_engaged()
        
        # Failure due to target disengagement during `hold_b`.
        self.trigger('target_disengaged', expected_state='failure')
        
        # Teardown.
        self._trigger_failure_timeout()
    
    def test_move_a_failure(self):
        """ Verify a trial sequence that results in a hold B failure. """
        
        # Trial sequence.
        self._trigger_end_block()
        self._trigger_start_block()
        self._trigger_intertrial_timeout()
        
        # Failure due to target disengagement during `hold_b`.
        self.trigger('timeout', expected_state='failure')
        
        # Teardown.
        self._trigger_failure_timeout()
    
  

# Main.
if __name__ == '__main__': unittest.main()


