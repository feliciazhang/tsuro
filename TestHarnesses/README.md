# Test Harnesses

This directory holds test harnesses for our implementation of a Tsuro tournament. The test harnesses are ways of running integration tests across increasingly large portions of this codebase. See the various assignments for full documentation of the expected input format for the test harnesses. 

The test harness code is placed inside of the Tsuro directory (rather than `3/`, `4/`, etc) in order to ensure that it can typecheck. Placing the code in the numbered directories would mean that imports would not be able to work properly and thus mypy would not be able to be fully used. 
