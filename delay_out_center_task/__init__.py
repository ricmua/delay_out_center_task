""" State machine and model for a cursor-based center-out, out-center 
    behavioral task, with a delay period after the initial hold.

Examples
--------

TBD.

"""

# Copyright 2022 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Define the version.
__version__ = '1.0.0'

# Import local objects.
from .model import Model
from .machine import Machine
from .machine import states
from .machine import state_transitions
from .environment import Environment

# Run doctests.
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
    
  


