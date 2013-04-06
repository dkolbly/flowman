#! /bin/bash
#
#  Set up a family of repositories that we will use for unit testing
#  the pullq example
#

# Repository root; this represents the central repository

RR=/tmp/flowman-pullq-example-repo
rm -rf ${RR}
mkdir -p ${RR}

# Create a central "integration" repository

hg init ${RR}/integrate
cp examples/pullq/unittest-setup.sh ${RR}/integrate/setup.sh
hg -R ${RR}/integrate add ${RR}/integrate/setup.sh
hg -R ${RR}/integrate commit -m"Initial checkin"
cp examples/pullq/pave.py ${RR}/integrate/pave.py
hg -R ${RR}/integrate add ${RR}/integrate/pave.py
hg -R ${RR}/integrate commit -m"Added another file"
echo '# this is a test' >> ${RR}/integrate/pave.py
hg -R ${RR}/integrate commit -m"Updated a file"

# Create two branch clones

hg clone ${RR}/integrate ${RR}/donovan
hg clone ${RR}/integrate ${RR}/lane

# make a change in the branch clone

echo '# this is another test' >> ${RR}/donovan/pave.py
hg -R ${RR}/donovan commit -m"Added a line to DONOVAN"

# make a different change in the other clone

echo '# this a simpler test' >> ${RR}/lane/setup.sh
hg -R ${RR}/lane commit -m"Added something to LANE"

