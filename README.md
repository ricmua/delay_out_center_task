---
title: README
author: a.whit ([email](mailto:nml@whit.contact))
date: September 2022
---

<!-- License

Copyright 2022 Neuromechatronics Lab, Carnegie Mellon University (a.whit)

Created by: a. whit. (nml@whit.contact)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.
-->

# Delayed out-center behavioral task

This package contains a state machine and model for a cursor-based behavioral 
task. It is intended primarily for use in experimental science. It is derived 
from the classic [center-out task] paradigm of behavioral neurophysiology -- 
which has most notably been employed in the study of [neural codes] in 
[motor cortex]. The task requires a user to move a cursor between visual 
targets that are positioned throughout a three-dimensional workspace. 

This task framework is designed to be compatible with the [pytransitions] 
package for Python state machines.

See the [examples](#example) for a quick introduction. More extensive examples 
and [doctest]s are provided as comments in the source code (e.g., 
[model.py](delay_out_center_task/model.py)).

<!--
## Organization

The task framework is composed of th
-->

<!--
```
import doctest
doctest.testfile('README.md', module_relative=False)
```
-->

## Task overview

In this version of the task paradigm, intervals of time and sequences of 
movement are divided into [trial](doc/markdown/trials.md)s. A trial represents 
one attempt at a fixed behavioral objective. If the user meets all of the 
conditions of the objective during a trial period, then the trial is considered 
a success, and a [rewarding outcome] is typically rendered. For this task, the 
success conditions require a user to move the cursor from some "center" target 
to a randomly-selected "outer" target, and back again. As the names imply, the 
center target is typically placed at the origin of the 3D space, and the outer 
targets are positioned near the periphery. The user is expected to hold for a 
short interval at each target, and to wait for a short delay interval after the 
initial presentation of the outer target.

## Modifications

This task framework is intended to be forked and extended. Please 
[contact the author](mailto:nml@whit.contact) if you make modifications or 
design new tasks.

## Example

Perhaps the best way to introduce the package and task is via an example. This 
example is provided in [doctest] format, and can be run via the following 
code:[^python_paths]

[^python_paths]: Provided that the package is installed, or the [Python path] 
                 is otherwise set appropriately.

```
import doctest
doctest.testfile('README.md', module_relative=False)

```

Import the task components parts.

```python
>>> from delay_out_center_task import Environment
>>> from delay_out_center_task import Model
>>> from delay_out_center_task import Machine

```

For the purpose of this example, override the `timeout` trigger function, to 
disable automatic state transitions, and facilitate manual interaction with the 
state machine.

```python
>>> Model.timeout = lambda s, *a, **k: None

```

Also disable event reporting, to improve clarity.

```python
>>> Machine.log_event = lambda s, d: None

```

Initialize the task components: an environment interface, a model, and a 
machine.

```python
>>> environment = Environment()
>>> model = Model(environment=environment)
>>> machine = Machine(model=model)

```

Upon initialization, the environment contains only a spherical cursor object.

```python
>>> list(environment.objects)
['cursor']

```

Activate the state machine and start a block of trials. At the start of each 
block, a set of possible outer target parameters is loaded. Here, we are using 
the default set, which places targets at the corners and on the faces of a 
square centered at the origin.

```python

>>> # Verify the current state.
>>> model.state
'inactive'

>>> # Start a block of trials.
>>> success = model.start_block()
State: intertrial

>>> # Verify that a set of target parameters was loaded.
>>> len(model.targets)
8
>>> model.targets[0]['position']
(1.0, 0.0, 0.0)

```

The `intertrial` state is a brief delay between trials that automatically
transitions to the `trial_setup` state, after a brief delay. During trial setup 
a target is initialized in the environment, and a set of target parameters 
(i.e., a behavioral objective for the trial) are chosen. The trial setup state 
transitions automatically to the initial state in a trial sequence. For this 
task, the first trial state is `move_a`.[^double_reporting]

[^double_reporting]: Due to the idiosyncrasies of the [pytransitions] package, 
                     states that transition automatically are not correctly 
                     reported. Instead, the next state is logged twice. This 
                     is because state logging occurs after a state transition 
                     is complete, and automatic transitions occur _during_ the 
                     transition.

```python

>>> # Verify that no target sphere exists in the environment.
>>> target_index = model.target_index
>>> environment.exists('target')
False

>>> # Transition through the trial_setup state
>>> # into the move_a state.
>>> success = model.trigger('timeout')
State: move_a
State: move_a

>>> # Two state transitions are reported.
>>> # The first reported transition is incorrectly 
>>> # logged as move_a instead of trial_setup.

>>> # Verify that a target sphere now exists in the 
>>> # environment, and that a new target parameters 
>>> # index has been randomly chosen.
>>> environment.exists('target')
True
>>> model.target_index == target_index
False

```

To satisfy the success conditions of the `move_a` task state, the user must 
move the cursor to engage the target. This causes the task to transition to the 
`hold_a` state. The hold state requires that the user maintain engagement with 
the target for a brief interval. When the hold interval times out, the task 
transitions to the `delay_a` state. A cue appears at an outer target position. 
The cue resembles a target sphere, but has a different color. 

```python

>>> # Transition to the hold_a state.
>>> success = model.target_engaged()
State: hold_a

>>> # Verify that no cue exists.
>>> environment.exists('cue')
False

>>> # Transition to the delay_a state.
>>> # A cue sphere appears.
>>> success = model.trigger('timeout')
State: delay_a
>>> environment.exists('cue')
True

```

During the delay period, the target sphere remains at the center position, and 
the user is expected to engage with the target for the duration of the period. 
When the period expires, the cue disappears, and the task transitions to the 
`move_b` state. At this point, the target is moved to the position formerly 
occupied by the cue sphere.

```python

>>> # Record the state of the target and cue before the transition.
>>> p_c = environment.get_position('cue')
>>> p_t = environment.get_position('target')

>>> # Transition to the move_b state.
>>> success = model.trigger('timeout')
State: move_b

>>> # The cue is extinguished.
>>> environment.exists('cue')
False

>>> # The target is moved to the cue position.
>>> environment.get_position('target') == p_t
False
>>> environment.get_position('target') == p_c
True

```

The `move_b` and `hold_b` task states are nearly identical to the `move_a` and 
`hold_a` states. The same is true for `move_c` and `hold_c`, except that the 
target is returned to the center position.

```python

>>> # Transition to the hold_b state.
>>> success = model.target_engaged()
State: hold_b

>>> # Transition to the move_c state.
>>> success = model.trigger('timeout')
State: move_c

>>> # The target is returned to the center position.
>>> environment.get_position('target') == (0.0, 0.0, 0.0)
True

>>> # Transition to the hold_c state.
>>> success = model.target_engaged()
State: hold_c

```

Upon successful completion of the hold state, the task transitions to the 
`success` state, wherein reinforcement is typically delivered. The success 
state automatically transitions to the `trial_teardown` state after a brief 
delay. During teardown, the target is removed from the workspace, and the task 
is returned to the intertrial state.[^double_reporting] This completes a 
successful trial. 

```python

>>> # Transition to the success state.
>>> success = model.trigger('timeout')
State: success

>>> # Transition to the trial_teardown state.
>>> success = model.trigger('timeout')
State: intertrial
State: intertrial

>>> # The target is returned to the center position.
>>> environment.exists('target')
False

```

A trial fails if the user does not meet a success condition for any trial 
state. This might occur, for example, if the user fails to engage with the 
target during a move period.

```python

>>> # Transition through the trial_setup state, 
>>> # and to the move_a states from intertrial.
>>> success = model.trigger('timeout')
State: move_a
State: move_a

>>> # The move state times out.
>>> success = model.trigger('timeout')
State: failure

>>> # Transition through the trial_teardown state,
>>> # to return to the intertrial state.
>>> success = model.trigger('timeout')
State: intertrial
State: intertrial

```

A trial might also result in failure if the user disengages from the target 
during a hold period.

```python

>>> # Transition through the trial_setup state, 
>>> # and to the move_a states from intertrial.
>>> success = model.trigger('timeout')
State: move_a
State: move_a

>>> # Transition to the hold_a state.
>>> success = model.target_engaged()
State: hold_a

>>> # The cursor disengages before the hold period expires.
>>> success = model.target_disengaged()
State: failure

>>> # Transition through the trial_teardown state,
>>> # to return to the intertrial state.
>>> success = model.trigger('timeout')
State: intertrial
State: intertrial

```

More extensive examples and [doctest]s are provided as comments in the source 
code (e.g., [machine.py](delay_out_center_task/machine.py)).

## Motivation and design philosophy

When designing a behavioral experiment, research scientists often build 
custom implementations that reproduce common task structure and logic.
Usually, these implementations are designed for a particular hardware system or 
graphical interface. The associated code often involves a mixture of low-level 
device programming and high-level task scripting. Usually, a state machine 
is used to organize the latter.

This package is intended to be a step toward [separation of concerns] in the 
implementation of behavioral experiments. In particular, the objective is to 
make the task logic and actions as independent as possible from the environment 
and middleware. In this way, we hope to encourage code / paradigm re-use, and 
to cut down on mistakes. Behavioral paradigms should be generalizable, across 
hardware setups. At the same time, task designers shouldn't get bogged down in 
low-level details each time they want to design a new experiment.

As a particular example of how this philosophy and approach might be realized, 
it is worthwhile to point out that this task has been designed to be compatible 
with the [ros_transitions] package. This means that this task can interface 
immediately with any hardware or software modules built for [ROS2]. For 
example, the [ros_force_dimension] package might be used to link the  
cursor to a Force Dimension haptic robot, which might be displayed in a 
[Unity3D] scene, via the ROS2-enabled [unity_spheres_environment].

It is important to reiterate that -- despite this potential for extension -- 
this remains a mostly self-contained package, and the task itself can be tested 
and modified entirely in isolation. The included prototype environment 
facilitates such development and testing (and, in turn, defines the 
expectations for any environment implementation; see 
[environment.py](delay_out_center_task/environment.py)). The best way to 
get to know the task framework is to clone a copy and mess around.

## License

Copyright 2022 [Neuromechatronics Lab][neuromechatronics], 
Carnegie Mellon University

Created by: a. whit. (nml@whit.contact)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

<!---------------------------------------------------------------------
   References
---------------------------------------------------------------------->

[Python path]: https://docs.python.org/3/tutorial/modules.html#the-module-search-path

[doctest]: https://docs.python.org/3/library/doctest.html

[rewarding outcome]: https://en.wikipedia.org/wiki/Reinforcement

[neural codes]: https://en.wikipedia.org/wiki/Neuronal_ensemble#Background

[motor cortex]: https://en.wikipedia.org/wiki/Primary_motor_cortex#Movement_coding

[center-out task]: https://pubmed.ncbi.nlm.nih.gov/3411362/

[pytransitions]: https://github.com/pytransitions/transitions

[doctest]: https://docs.python.org/3/library/doctest.html

[ros_transitions]: https://github.com/ricmua/ros_transitions

[separation of concerns]: https://en.wikipedia.org/wiki/Separation_of_concerns

[ros_force_dimension]: https://github.com/ricmua/ros_force_dimension

[ROS2]: https://docs.ros.org/en/humble/index.html

[Unity3D]: https://en.wikipedia.org/wiki/Unity_(game_engine)

[unity_spheres_environment]: https://github.com/ricmua/unity_spheres_environment


