""" Test the doctest blocks in the README.md file. """

# Copyright 2022 Carnegie Mellon University Neuromechatronics Lab (a.whit)
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# 
# Contact: a.whit (nml@whit.contact)


# Import standard Python packages.
from os.path import dirname

# Import doctest.
import doctest


# Define the absolute filepath for the README.
README_RELATIVE_FILEPATH = f'README.md'
README_ABSOLUTE_FILEPATH = f'{dirname(dirname(__file__))}/README.md'

# Define the test function.
def test_readme():
    """ Run the README.md doctests. """
    (failure_count, test_count) \
      = doctest.testfile(README_ABSOLUTE_FILEPATH, module_relative=False)
    print(f'Tests: {test_count}; Failures: {failure_count}')
    assert failure_count == 0
    
  

# Main.
if __name__ == '__main__': test_readme()

