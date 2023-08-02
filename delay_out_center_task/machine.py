""" State machine for a cursor-based center-out, out-center behavioral task, 
    with an imposed delay period after the first hold.

The `Machine` class defines a [pytransitions] state machine for a cursor task.

The task requires a cursor to engage a target in three-dimensional space, by 
moving to it and holding in position for a period of time. In each trial of the 
task, targets are first presented at a central "home" position, and then at a 
peripheral or "outer" position. To complete a trial successfully, a user must 
move to each of these targets, hold at each, and then return to the home 
position. A delay is imposed after the first hold, during which a cue appears 
at what will subsequently be the position of the outer target. The user is 
expected to continue holding at the home target during the delay.

[pytransitions]: https://github.com/pytransitions/transitions#-transitions

Examples
--------

For this example, suppress event logging for the sake of legibility.

>>> Machine.log_event = lambda s, d: None

Create a state machine, using the default arguments.

>>> machine = Machine()
>>> machine.state
'inactive'

Create a convenient function for triggering events and reporting the state. 
This is useful for simplifying the code in the examples that follow.

>>> def trigger(state): return getattr(machine.model, state)()

Start a block of trials.

>>> success = trigger('start_block')
State: intertrial

Once a block has started, the state machine is placed in the `intertrial` 
state. In general, a `start_trial` event must then be triggered manually, in 
order to start a trial. However, for this state machine, we've also defined a 
`timeout` trigger, such that the `intertrial` state can be configured to 
automatically transition to a new trial, after a brief delay.

A trial consists of a setup state, a series of task-specific trial states, and 
a teardown state. The `start_trial` event will cause the state machine to 
transition to the `trial_setup` state. This state exists only for the purpose 
of implementing actions or behaviors that are necessary for preparing a trial. 
It is expected that the model transition callbacks for this state will also 
trigger a manual transition to the first state in the trial sequence, which is 
task-specific. For this example, the first trial state is `hold_a`. Similarly, 
the final trial states -- which are almost always the `success` or `failure` 
states -- should transition to the `trial_teardown` state, which is intended 
for implementing post-trial housekeeping actions. This state should manually 
transition to the `intertrial` state (e.g., via the `end_trial` event).

Step through the state sequence for a successful trial.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('target_engaged')
State: hold_a
>>> success = trigger('timeout')
State: delay_a
>>> success = trigger('timeout')
State: move_b
>>> success = trigger('target_engaged')
State: hold_b
>>> success = trigger('timeout')
State: move_c
>>> success = trigger('target_engaged')
State: hold_c
>>> success = trigger('timeout')
State: success
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Step through the state sequence of a trial that fails during the `hold_c` phase.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('target_engaged')
State: hold_a
>>> success = trigger('timeout')
State: delay_a
>>> success = trigger('timeout')
State: move_b
>>> success = trigger('target_engaged')
State: hold_b
>>> success = trigger('timeout')
State: move_c
>>> success = trigger('target_engaged')
State: hold_c
>>> success = trigger('target_disengaged')
State: failure
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Step through the state sequence of a trial that fails during the `move_c` phase.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('target_engaged')
State: hold_a
>>> success = trigger('timeout')
State: delay_a
>>> success = trigger('timeout')
State: move_b
>>> success = trigger('target_engaged')
State: hold_b
>>> success = trigger('timeout')
State: move_c
>>> success = trigger('timeout')
State: failure
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Step through the state sequence of a trial that fails during the `hold_b` phase.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('target_engaged')
State: hold_a
>>> success = trigger('timeout')
State: delay_a
>>> success = trigger('timeout')
State: move_b
>>> success = trigger('target_engaged')
State: hold_b
>>> success = trigger('target_disengaged')
State: failure
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Step through the state sequence of a trial that fails during the `move_b` phase.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('target_engaged')
State: hold_a
>>> success = trigger('timeout')
State: delay_a
>>> success = trigger('timeout')
State: move_b
>>> success = trigger('timeout')
State: failure
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Step through the state sequence of a trial that fails during the `delay_a` 
phase.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('target_engaged')
State: hold_a
>>> success = trigger('timeout')
State: delay_a
>>> success = trigger('target_disengaged')
State: failure
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Step through the state sequence of a trial that fails during the initial 
`hold_a` phase.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('target_engaged')
State: hold_a
>>> success = trigger('target_disengaged')
State: failure
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Step through the state sequence of a trial that fails because it never engages 
with the target.

>>> success = trigger('timeout')
State: trial_setup
>>> success = machine.model.to_move_a()  # Manual transition to trial state 1.
State: move_a
>>> success = trigger('timeout')
State: failure
>>> success = trigger('timeout')
State: trial_teardown
>>> success = trigger('end_trial')
State: intertrial

Terminate the block of trials.

>>> success = trigger('end_block')
State: inactive
"""


# Copyright 2022 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Import the transitions state machine package.
import transitions
import transitions.extensions


# Define the states.
states \
    = ['inactive',
       'intertrial',
       'trial_setup',
       'failure',
       'success',
       'trial_teardown',
       'move_a',
       'hold_a',
       'delay_a',
       'move_b',
       'hold_b',
       'delay_b',
       'move_c',
       'hold_c',
      ]
"""
States of the prototype cursor task. 

As described in the pytransitions [documentation], states can be defined as 
`transitions.State` objects, strings (indicating the names of the states), or 
as dict records.

[documentation]: https://github.com/pytransitions/transitions#states
"""

# Define the state transitions.
setup = 'trial_setup'
teardown = 'trial_teardown'
state_transitions \
    = [dict(trigger='start_block', source='inactive',   dest='intertrial'),
       dict(trigger='start_trial', source='intertrial', dest='trial_setup'),
       dict(trigger='timeout',     source='intertrial', dest='trial_setup'),
       dict(trigger='timeout',     source='failure',    dest=teardown),
       dict(trigger='timeout',     source='success',    dest=teardown),
       dict(trigger='end_trial',   source=teardown,     dest='intertrial'),
       dict(trigger='end_block',   source='*',          dest='inactive'),
      ] \
    + [
       dict(trigger='target_engaged',    source='move_a',     dest='hold_a'),
       dict(trigger='timeout',           source='move_a',     dest='failure'),
       dict(trigger='timeout',           source='hold_a',     dest='delay_a'),
       dict(trigger='target_disengaged', source='hold_a',     dest='failure'),
       dict(trigger='timeout',           source='delay_a',    dest='move_b'),
       dict(trigger='target_disengaged', source='delay_a',    dest='failure'),
       dict(trigger='target_engaged',    source='move_b',     dest='hold_b'),
       dict(trigger='timeout',           source='move_b',     dest='failure'),
       dict(trigger='timeout',           source='hold_b',     dest='delay_b'),
       dict(trigger='target_disengaged', source='hold_b',     dest='failure'),
       dict(trigger='timeout',           source='delay_b',    dest='move_c'),
       dict(trigger='target_disengaged', source='delay_b',    dest='failure'),
       dict(trigger='target_engaged',    source='move_c',     dest='hold_c'),
       dict(trigger='timeout',           source='move_c',     dest='failure'),
       dict(trigger='timeout',           source='hold_c',     dest='success'),
       dict(trigger='timeout',           source='move_c',     dest='failure'),
       dict(trigger='target_disengaged', source='hold_c',     dest='failure'),
      ]
"""
State transitions of the delayed center-out, out-center cursor task.

State [transitions] are most readily specified as dict records. Each record 
should contain the following keys:

* `trigger`
* `source`
* `dest`

The transitions defined here fall into three categories:

* Those that are related to task management / segmentation;
* Those that are related to the task objectives and behaviors;
* Those that implement internal state machine transitions.

[transitions]: https://github.com/pytransitions/transitions#transitions
"""


# For convenience, define a model class.
#class Machine(transitions.extensions.LockedMachine):
class Machine(transitions.Machine):
    """
    State machine for the prototype cursor task.
    
    This class is equivalent to the [pytransitions] Machine class, but with 
    a pre-defined set of states and transitions defined by the module variables
    :py:attr`states` and :py:attr`state_transitions`.
    
    [pytransitions]: https://github.com/pytransitions/transitions#-transitions
    
    See Also
    --------

    model.Model : Prototype model associated with this state machine.
    """
    def __init__(self, *args,
                       states=states,
                       transitions=state_transitions,
                       initial='inactive',
                       **kwargs):
        kwargs = {'states': states, 
                  'transitions': transitions, 
                  'initial': initial,
                  'ignore_invalid_triggers': True, # 
                  'send_event': True,
                  'prepare_event': self.log_event,
                  'after_state_change': self.log_state_change,
                  **kwargs}
        super().__init__(*args, **kwargs)
        self._verbose = False
        
    def log(self, message, severity=None): 
        """ Record a message in the log. """
        print(message, flush=True)
        
    def log_state_change(self, event_data):
        """ Log changes in the state machine state.
        
        This function records the state change to the internal log. The 
        structure of the event_data argument is dictated by the pytransitions 
        package. To suppress messages sent to the internal log, adjust the ROS 
        log severity.
        """
        state = self.model.state
        self.log(f'State: {state}')
        is_internal = not bool(event_data.transition.dest)
        
    def log_event(self, event_data):
        """ Log events or triggers that cause changes in the state machine.
        
        This function records events to the internal log. The structure of 
        the event_data argument is dictated by the pytransitions package. To
        suppress messages sent to the internal log, adjust the ROS log severity.
        """
        self.log(f'Event: {event_data.event.name}')
    
  

# If invoked as a script, run the doctest.
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
  

