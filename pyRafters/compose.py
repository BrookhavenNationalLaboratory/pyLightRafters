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


def _proc_subtools(tool, input_edges, output_edges, args):
    """
    Collects inputs and runs the sub-tool

    Parameters
    ----------
    tool : ToolBase
        The Tool to run

    input_edges : dict
       keyed on ancestor tool instances, value is list of
       pairs of strings labeling connections between input/output

    output_edges : dict
       keyed on descendant tool instances.  value is list
       of pairs of strings labeling connections between input/output
    """
    # grab list of traits from tool
    params, srcs, snks = tool.tool_args()
    # loop over ancestor tools and link lists
    for back, links in six.iteritems(input_edges):
        # loop over links
        for snk_nm, src_nm in links:
            # get the sink from the ancestor
            print(back)
            print(snk_nm)
            print(src_nm)
            snk = getattr(back, snk_nm)
            # turn sink into source
            src = snk.make_source()
            # assign the source to the new sink
            setattr(tool, src_nm, src)

    # loop over the input args for the tool
    for arg_nm, arg_val in six.iteritems(args):
        setattr(tool, arg_nm, arg_val)

    # make sure we assign all of the sinks
    for arg in snks:
        if getattr(tool, arg.name) is None:
            setattr(tool, arg.name, _handler_map[arg.dtype]())
    # run the tool
    tool.run()
    pass


def _node_iter(G, g_inputs):
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
        # get input edges
        input_edges = G.in_edges(job)
        in_link_info = dict()
        # construct dict of useful information
        for parent, child in input_edges:
            print(parent, child)
            in_link_info[parent] = G[parent][child]['links']
        # get output edges
        output_edges = G.out_edges(job)
        out_link_info = dict()
        # construct dict of useful information
        for parent, child in output_edges:
            out_link_info[child] = G[parent][child]['links']
        # pull the tool args out of the global dict
        args = g_inputs[job]

        # push work off to helper function
        yield (job, in_link_info, out_link_info, args)


def run_graph(G, g_inputs):
    for node_data in _node_iter(G, g_inputs):
        _proc_subtools(*node_data)
