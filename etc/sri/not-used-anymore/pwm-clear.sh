#!/bin/bash

# Disable all PWMs
find /sys/devices/platform/ocp/483* -type f -name enable -exec sh -c "echo 0 > {}" \;

# Now remove all exports
#find /sys/devices/platform/ocp/483* -type f -name unexport -exec sh -c "echo 1 > {}" \;
#find /sys/devices/platform/ocp/483* -type f -name unexport -exec sh -c "echo 0 > {}" \;
