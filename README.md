pyLight_tools
=============

Interface layer for CT image processing tools.

[![Build Status](https://travis-ci.org/BrookhavenNationalLaboratory/pyLightRafters.png?branch=master)](https://travis-ci.org/BrookhavenNationalLaboratory/pyLightRafters)

Base Classes
------------

This project contains base classes to provide a common self-describing
interface for calling image analysis `Tools`.

class family | purpose | module
------------ | ------- | ------
data handlers | to abstract away the backing method of data storage | `pylight_tools.data_base`
`ArgSpec` | container for all the meta-data about arguments | `pylight_tools.args_base`
`ToolBase` | container for all of the meta-data + code to run a given computation | `pylight_tools.tools_base`

Handlers
--------

The idea of handlers is to provide a layer between the `Tool` code and
the details of how the data is to be stored.  There will be a
sub-class of `BaseSource`/`BaseSink` for each semantic type of data.
Tools validate their data I/O by requiring that arguments be of a
specific sub-class.  For example the class `DistributionSource`
provides the functions:

 - `read_values()`
 - `read_edges()`

which return, respectively, the value and each bin and the left edges
of the bins.  A `Tool` that needs a distribution as input can thus
take a `DistributionSource` instance and work correctly, independent
of the details of exactly how the data is stored.


Eventually, the `handlers` module should include reference
implementations for all of the data types that can be stored in hdf files.

`ArgSpec`
---------

These classes provide enough meta-data about the arguments
(parameters, input data, output data) to auto-generate user interfaces
from the `Tool` class.


Example Tools
-------------



The tools in `pylight_tools.tools` are intended to provide a template for adding new tools.
