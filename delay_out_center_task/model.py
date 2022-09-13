""" State machine model for a center-out, out-center behavioral task, with a 
    delay period following the initial hold.

Examples
--------

The model class expects an interface with the behavioral environment. For this 
purpose, import a minimalist class that simply keeps track of the position 
of a spherical target in a 3D space. In general, the interface with the 
environment will depend on the task context.

>>> from .environment import Environment

Declare additional functionality for verifying timeout intervals. This is just 
a covenient way to demonstrate that the task delays are behaving as we expect 
them to.

>>> from time import time
>>> def time_timeout(fun, *args, **kwargs):
...     t0 = time()
...     fun(*args, **kwargs)
...     model.timeout_timer.join()
...     return time() - t0
>>> tol = 0.005 # 5ms

When used in conjunction with a pytransitions state machine, the `trigger` 
function will automatically be added to the model class. However, this example 
tests the model in isolation, and does not use the pytransitions framework. In 
order to illustrate use of the model, define a derived class that implements 
the trigger function. This class prints a string whenever an event occurs.

>>> Model.trigger = lambda self, s: print(f'Trigger: {s}')
>>> Model.to_move_a = lambda self: 'move_a'

Accept the default values for the remaining arguments, and create the model 
class.

>>> environment = Environment()
>>> model = Model(environment=environment)

Upon initialization, the environment should contain a cursor sphere with 
default attribute values.

>>> environment.get_radius('cursor')
1.0
>>> environment.get_position('cursor')
(0.0, 0.0, 0.0)
>>> environment.get_color('cursor')
(0.0, 0.0, 0.0, 1.0)

No other objects should be present in the environment, at this time, but 
spheres can be initialized and destroyed when required. Verify this mechanism.

>>> len(environment.objects) == 1
True
>>> environment.initialize_sphere(key='test')
>>> len(environment.objects) == 2
True
>>> environment.get_radius('test')
1.0
>>> environment.get_position('test')
(0.0, 0.0, 0.0)
>>> environment.destroy_sphere(key='test')
>>> len(environment.objects) == 1
True
>>> try: environment.get_position('test')
... except KeyError: print('Object does not exist')
Object does not exist

The state machine model implements some basic functionality for working in the 
environment. For example, it provides a function for setting a timeout timer, 
relative to the environment's clock. Verify the timer functionality.

>>> delta = time_timeout(model.set_timeout, timeout_s=0.100)
Trigger: timeout
>>> abs(delta - 0.100) < 0.01
True

This class also includes a convenience function for setting timeouts based on 
parameter values. In this example, the parameters have been set to default 
values. Verify that the parameterized timeout for the `move_a` state matches 
what is expected from the parameter value.

>>> delta = time_timeout(model.set_parameterized_timeout, key='move_a')
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.move_a']) < tol
True

When the model is activated, a block of trials commences. At this time, the 
model loads a list of target parameter records. Each trial of the task 
represents an opportunity for a subject to move to a new target chosen from 
this list. The color of the cursor is also set. Verify the target set.

>>> model.on_exit_inactive()
>>> len(model.targets)
8
>>> model.targets[0]['position']
(1.0, 0.0, 0.0)
>>> environment.get_color()
(0.0, 1.0, 0.0, 1.0)

The intertrial period is a brief delay between trials, during which the user is 
not provided with any prompts or expected to take any directed actions. Verify 
that a timer timer is set upon entering this state.

>>> delta = time_timeout(model.on_enter_intertrial)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.intertrial']) < tol
True
>>> model.on_exit_intertrial()

Before a trial begins, the task model chooses a behavioral objective and 
prepares the environment. Verify that a new target is initialized in the 
environment, and that new behavioral target parameters are chosen. Also confirm 
that the model manually requests a transition to the `move_a` state, once the 
trial is set up. The target is colored blue, with partial transparency.

>>> target_index = model.target_index
>>> environment.exists('target')
False
>>> model.on_enter_trial_setup()
>>> environment.exists('target')
True
>>> model.target_index == target_index
False
>>> environment.get_color('target')
(0.0, 0.0, 1.0, 0.5)

The first trial state in this task is the `move_a` state. During this state, a 
target is presented to the user at a "home" or "center" position. Here, the 
home position is set to the origin in the 3-dimensional space represented by 
the environment. The user is expected to engage the presented target. Verify 
that the target is moved to the home position upon entering the `move_a` state, 
and that the state times out after a specified interval.

>>> delta = time_timeout(model.on_enter_move_a)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.move_a']) < tol
True
>>> environment.get_position('target') == (0.0, 0.0, 0.0)
True
>>> model.on_exit_move_a()

Upon successful completion of the `move_a` state objectives, the task is 
expected to transition into the `hold_a` state. This state requires that the 
user continue engaging the target for a specified amount of time. Verify the 
`hold_a` timeout.

>>> delta = time_timeout(model.on_enter_hold_a)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.hold_a']) < tol
True
>>> environment.get_position('target') == (0.0, 0.0, 0.0)
True
>>> model.on_exit_hold_a()

After successful completion of the `hold_a` state, the task is expected to 
transition into the `delay_a` state. This is an imposed behavioral delay. At 
the start of the delay period, a "cue" target is initialized at some new 
position. However, the user is expected to maintain engagement the home target 
for the duration of the `delay_a` state. The cue disappears as the state 
expires. The cue is colored red, with partial transparency.

>>> environment.exists('cue')
False
>>> delta = time_timeout(model.on_enter_delay_a)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.delay_a']) < tol
True
>>> environment.exists('cue')
True
>>> environment.get_color('cue')
(1.0, 0.0, 0.0, 0.5)
>>> environment.get_position('cue') == environment.get_position('target')
False
>>> model.on_exit_delay_a()
>>> environment.exists('cue')
False

The `move_b` period is similar to the `move_a` period, except the target is 
moved to an "outer" position (i.e., a position that is not the "center" or 
"home" position). The user is expected to move the cursor to re-engage with the 
target.

>>> delta = time_timeout(model.on_enter_move_b)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.move_b']) < tol
True
>>> environment.get_position('target') == (0.0, 0.0, 0.0)
False
>>> model.on_exit_move_b()

The `hold_b` state is nearly identical to the `hold_a` state.

>>> delta = time_timeout(model.on_enter_hold_b)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.hold_b']) < tol
True
>>> model.on_exit_hold_b()

The `move_c` period is nearly identical to the `move_a` period. The target is 
returned to the center or home position upon entering the state. The user is 
again expected to move the cursor to re-engage with the target.

>>> delta = time_timeout(model.on_enter_move_c)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.move_c']) < tol
True
>>> environment.get_position('target') == (0.0, 0.0, 0.0)
True
>>> model.on_exit_move_c()

The `hold_c` state is nearly identical to the `hold_a` and `hold_b` states.

>>> delta = time_timeout(model.on_enter_hold_c)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.hold_c']) < tol
True
>>> model.on_exit_hold_c()

If the user satisifies all of the conditions in each of these trial states, 
then the trial is considered successful, and the task enters the `success` 
state. Otherwise, the task enters the `failure` state. Both states terminate 
after a short delay. The delay for the `failure` state is generally set to a 
longer duration, in order to impose a penalty.

>>> delta = time_timeout(model.on_enter_success)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.success']) < tol
True
>>> model.on_exit_success()
>>> delta = time_timeout(model.on_enter_failure)
Trigger: timeout
>>> abs(delta - model.parameters['timeout_s.failure']) < tol
True
>>> model.on_exit_failure()

Both the `success` and `failure` states transition to a trial teardown state. 
As the trial ends, the target is destroyed.

>>> environment.exists('target')
True
>>> model.on_enter_trial_teardown()
Trigger: end_trial
>>> environment.exists('target')
False

The task then moves to the inter-trial state, and then to a new trial.
"""

# Copyright 2022 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Imports.
import yaml
import numpy.random


# Define the default target set.
default_targets \
  = [dict(position=(+1.0, +0.0, +0.0)),
     dict(position=(+0.0, +1.0, +0.0)),
     dict(position=(+1.0, +1.0, +0.0)),
     dict(position=(-1.0, -0.0, +0.0)),
     dict(position=(-0.0, -1.0, +0.0)),
     dict(position=(-1.0, -1.0, +0.0)),
     dict(position=(+1.0, -1.0, +0.0)),
     dict(position=(-1.0, +1.0, +0.0)),
    ]
""" Default center-out, out-center target set, with outer targets positioned 
    at the corners and faces of a square.

This default set defines "outer" targets at the corners and faces of a square 
centered at the origin. This is useful for basic task operations and testing.

This also serves as an example of the structure expected in the YAML file 
stored at the path specified by the optional parameter `paths.target_file`.
"""


# Define the task model.
class Model:
    """ Delayed center-out, out-centers cursor task model prototype.
    
    The "model" terminology -- used to refer to the class to be managed by the 
    state machine -- is derived from the documentation for the pytransitions 
    package.
    
    Parameters
    ----------
    
    environment
        An object representing the environment containing the cursor and 
        target. This provides the interface via which the model can manipulate 
        the state of the cursor and/or targets.
    parameters : collections.abc.MutableMapping
        A mapping between parameter keys and values.
    log : callable
        A callable that provides a mechanism for logging status messages.
    
    See Also
    --------
    
    machine.Machine : Center-out state machine associated with this model.
    """
    
    def __init__(self, environment, parameters={}, log=None):
        self._prng = numpy.random.default_rng()
        self.environment = environment
        self.log = log if log else lambda m: print(m, flush=True)
        self.initialize_parameters(parameters)
        self.load_targets()
        
    def initialize_parameters(self, parameters):
        """ Declare and set defaults for all parameters used in the cursor task.
        
        Parameters
        ----------
        parameters : dict-like
            A mutable mapping between parameters keys -- of string type -- and 
            parameters values.
        """
        
        # Initialize local parameters via arguments.
        self.parameters = parameters
        
        # Establish shorthand.
        set_default = self.parameters.setdefault
        
        # Initialize default timeout parameters.
        set_default('timeout_s.move_a',     2.000)
        set_default('timeout_s.hold_a',     0.500)
        set_default('timeout_s.delay_a',    0.500)
        set_default('timeout_s.move_b',     1.000)
        set_default('timeout_s.hold_b',     0.500)
        set_default('timeout_s.move_c',     1.000)
        set_default('timeout_s.hold_c',     0.500)
        set_default('timeout_s.failure',    0.200)
        set_default('timeout_s.success',    0.000)
        set_default('timeout_s.intertrial', 0.010)
        
        # Set target file path.
        set_default('paths.targets', None) #'config/targets.yaml')
        
    def set_parameterized_timeout(self, key, **kwargs):
        """ Request that the timer invoke the timeout callback after a delay 
            specified by a parameter.
        
        Parameters
        ----------
        key : string
            Key or label used to identify the parameter in the `timeout_s` 
            parameter namespace or tree.
        **kwargs : dict
            Keyword arguments for the `set_timeout` function.
        """
        timeout_s = self.parameters[f'timeout_s.{key}']
        if timeout_s <= 0: self.trigger('timeout')
        else: self.set_timeout(timeout_s=timeout_s)
        
    def set_timeout(self, timeout_s, callback=None, start=True):
        """ Request that the timer invoke the timeout callback after the 
            specified delay.
        
        Parameters
        ----------
        timeout_s : float
          Desired time delay, in seconds.
        callback : callable
          Callback to invoke when the timer expires. Defaults to the `timeout` 
          member, if no argument is provided.
        start : bool
          Specify false to setup the timer without starting it.
        """
        callback = callback if callback else self.timeout
        self.timeout_timer = self.environment.timer(timeout_s, callback)
        if start: self.timeout_timer.start()
        
    def cancel_timeout(self):
        """ Cancel any timeout timer that might be set. """
        
        # Cancel the timer if it is set.
        if self.timeout_timer.is_alive(): self.timeout_timer.cancel()
        
    def timeout(self, *args, **kwargs):
        """ Timeout trigger function. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
        # Trigger the timeout event.
        return self.trigger('timeout')
    
    def load_targets(self, filepath=''):
        """ Load target parameters from file, or a default constant.
        
        Target parameters are stored in records format (i.e., a list of 
        mappings). At minimum, a target record must specify the position of the 
        target in space.
        
        Arguments
        ---------
        filepath : string, optional
            If specified, this path string points to a YAML file containing 
            target records.
        """
        
        # Load targets from a YAML file, if a file path is provided.
        filepath = filepath \
                   if filepath \
                   else self.parameters.get('file_path.targets', None)
        self.targets = yaml.safe_load(filepath) \
                       if filepath \
                       else default_targets
        
        # Set a random target index.
        self.target_index = None #self.choose_random_target_index()
        
    def choose_random_target_index(self):
        """ Set the current target index to a (uniformly) randomly-chosen index 
            into the list of target parameter records.
        """
        return self._prng.integers(len(self.targets))
        
    def set_home_target(self):
        """ Set the home (or "center") target parameters.
        """
        
        # Move the target to the home position.
        # For now, this is hard-coded as the origin.
        target = dict(position=(0.0, 0.0, 0.0))
        xyz = target['position']
        self.environment.set_position(*xyz, key='target')
        
    def on_enter_inactive(self, event_data=None):
        """ Initialize the "inactive" state. """
        pass
        
    def on_exit_inactive(self, event_data=None):
        """ Terminate the "inactive" state. """
        
        # Load the set of possible targets.
        self.load_targets()
        
        # Set the cursor color.
        self.environment.set_color(g=1.0, key='cursor')
        
    def on_enter_intertrial(self, event_data=None):
        """ Initialize the "intertrial" state.
        
        Usually, a task will cycle through the intertrial state automatically, 
        proceeding to the next trial after a short delay. However, although the 
        timeout parameter is declared, and the timeout timer is set here, the 
        transition itself is not defined by default. Derived classes should add 
        this to the list of state transitions, if automatic an transition is 
        desired.
        """
        
        # Set the timeout timer.
        self.set_parameterized_timeout('intertrial')
        
    def on_exit_intertrial(self, event_data=None):
        """ Terminate the "intertrial" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_trial_setup(self, event_data=None):
        """ Set up a trial.
        
        This method is invoked at the start of each trial and is intended for 
        any setup required for a trial. By default, the only action is to 
        create a target. Derived classes should override this state to 
        implement some sort of automatic transition to the task-specific 
        initial state of a trial.
        """
        
        # Create the target.
        self.environment.initialize_sphere('target')
        
        # Set the target color.
        self.environment.set_color(b=1.0, a=0.5, key='target')
        
        # Set a random target index.
        self.target_index = self.choose_random_target_index()
        
        # Insert an automatic transition to the initial, task-specific state 
        # of a trial.
        self.to_move_a()
        
    def on_enter_trial_teardown(self, event_data=None):
        """ Tear-down a trial.
        
        This method is invoked at the end of each trial and is intended for 
        any cleanup or tear-down operations required after completion of a 
        trial. By default, this state automatically transitions to the 
        intertrial state. The target is also destroyed.
        """
        
        # Clear the target.
        self.environment.destroy_sphere('target')
        
        # Automatically transition to the intertrial state.
        self.trigger('end_trial')
    
    def on_enter_move_a(self, event_data=None):
        """ Initialize the "move_a" state. """
        
        # Move the target to the home position.
        self.set_home_target()
        
        # Set the timeout timer.
        self.set_parameterized_timeout('move_a')
        
    def on_exit_move_a(self, event_data=None):
        """ Terminate the "move_a" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_hold_a(self, event_data=None):
        """ Initialize the "hold_a" state. """
        
        # Set the timeout timer.
        self.set_parameterized_timeout('hold_a')
        
    def on_exit_hold_a(self, event_data=None):
        """ Terminate the "hold_a" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_delay_a(self, event_data=None):
        """ Initialize the "delay_a" state. """
        
        # Set the timeout timer.
        self.set_parameterized_timeout('delay_a')
        
        # Initialize the cue.
        self.environment.initialize_sphere('cue')        
        
        # Set the cue position.
        target = self.targets[self.target_index]
        xyz = target['position']
        self.environment.set_position(*xyz, key='cue')
        
        # Set the cue color.
        self.environment.set_color(r=1.0, a=0.5, key='cue')
        
    def on_exit_delay_a(self, event_data=None):
        """ Terminate the "delay_a" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
        # Initialize the cue.
        self.environment.destroy_sphere('cue')        
        
    def on_enter_move_b(self, event_data=None):
        """ Initialize the "move_b" state. """
        
        # Set the outer target position.
        target = self.targets[self.target_index]
        xyz = target['position']
        self.environment.set_position(*xyz, key='target')
        
        # Set the timeout timer.
        self.set_parameterized_timeout('move_b')
        
    def on_exit_move_b(self, event_data=None):
        """ Terminate the "move_b" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_hold_b(self, event_data=None):
        """ Initialize the "hold_b" state. """
        
        # Set the timeout timer.
        self.set_parameterized_timeout('hold_b')
        
    def on_exit_hold_b(self, event_data=None):
        """ Terminate the "hold_b" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_move_c(self, event_data=None):
        """ Initialize the "move_c" state. """
        
        # Move the target to the home position.
        self.set_home_target()
        
        # Set the timeout timer.
        self.set_parameterized_timeout('move_c')
        
    def on_exit_move_c(self, event_data=None):
        """ Terminate the "move_c" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_hold_c(self, event_data=None):
        """ Initialize the "hold_c" state. """
        
        # Set the timeout timer.
        self.set_parameterized_timeout('hold_c')
        
    def on_exit_hold_c(self, event_data=None):
        """ Terminate the "hold_c" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_success(self, event_data=None):
        """ Initialize the "success" state. """
        
        # Set the timeout timer.
        self.set_parameterized_timeout('success')
        
    def on_exit_success(self, event_data=None):
        """ Terminate the "success" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
        
    def on_enter_failure(self, event_data=None):
        """ Initialize the "failure" state. """
        
        # Set the timeout timer.
        self.set_parameterized_timeout('failure')
                
    def on_exit_failure(self, event_data=None):
        """ Terminate the "failure" state. """
        
        # Reset the timeout timer.
        self.cancel_timeout()
    
  

# Run doctests.
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
    
  


