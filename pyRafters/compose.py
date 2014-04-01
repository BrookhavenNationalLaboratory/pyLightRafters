"""
Tools to execute and manage Directed Acylic Graphs (DAG) of tools.
"""


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import networkx as nx
import numpy as np
import six

from pyRafters.handlers.np_handler import NPImageSink
from pyRafters.handler_base import ImageSink

_handler_map = {ImageSink: NPImageSink}


def _proc_subtools(G, tool, args):
    """
    Collects inputs and runs the sub-tool

    Parameters
    ----------
    G : nx.DiGraph
        The topology of the tool

    tool : ToolBase
        The sub-component to run

    global_input : dict?
        The input to the DAG
    """
    # grab list of traits from tool
    params, srcs, snks = tool.tool_args()

    # grab input edges to this tool
    input_edges = G.in_edges(tool)

    # grab the source/snk connections from each edge
    for back, this in input_edges:

        for snk_nm, src_nm in G[back][this]['links']:
            snk = getattr(back, snk_nm)
            # turn sinks to sources
            src = snk.make_source()
            setattr(this, src_nm, src)

    # sort out what global input this tool has
    for arg_nm, arg_val in six.iteritems(args[tool]):
        setattr(tool, arg_nm, arg_val)

    # make sure we assign all of the sinks
    for arg in snks:
        if getattr(tool, arg.name) is None:
            setattr(tool, arg.name, _handler_map[arg.dtype]())
    # run the tool
    tool.run()
    pass


def run_graph(G, g_inputs):
    """
    Run a graph

    G : nx.DiGraph
       Nodes are tools, edges contain attribute 'link' which
       is a list of A -> B pairs for connecting the inputs
       and outputs

    g_inputs : dict
       Global inputs to tools.  Keyed on tool
       instances, values are dicts keyed on name
       of input values
    """
    # sort the tools by topological order so all needed inputs are
    # available
    for job in nx.topological_sort(G):
        # call helper function to actually do the work
        _proc_subtools(G, job, g_inputs)
