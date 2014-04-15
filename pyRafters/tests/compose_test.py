from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import networkx as nx
import numpy as np

from pyRafters.tools.basic import AddImages
from pyRafters.tools.examples import ImageHistogram

from pyRafters.compose import run_graph

from pyRafters.handlers.np_handler import NPImageSource
from pyRafters.handlers.base_file_handlers import OpaqueFigure

from testing_helpers import namedtmpfile
from numpy.testing import assert_array_equal


@namedtmpfile('png', 2)
def test_compose(f1, f2):
    G = nx.DiGraph()
    G.clear()
    add0 = AddImages()
    add1 = AddImages()
    hist0 = ImageHistogram()
    hist1 = ImageHistogram()

    G.add_node(add0)
    G.add_node(add1)
    G.add_node(hist0)
    G.add_node(hist1)

    shape = (256, 256)

    data0 = np.ones(shape).reshape((1, ) + shape)
    data1 = 2 * np.ones(shape).reshape((1, ) + shape)
    data2 = 3 * np.ones(shape).reshape((1, ) + shape)

    src0 = NPImageSource(data0)
    src1 = NPImageSource(data1)
    src2 = NPImageSource(data2)

    fig0 = OpaqueFigure(f1)
    fig1 = OpaqueFigure(f2)
    g_args = {add0: {'A': src0,
                     'B': src1},
              add1: {'B': src2},
              hist0: {'out_file': fig0},
              hist1: {'out_file': fig1},
            }

    G.add_edge(add0, add1, links=(('out', 'A'),) )
    G.add_edge(add0, hist0, links=(('out', 'input_file'),) )
    G.add_edge(add1, hist1, links=(('out', 'input_file'),) )

    run_graph(G, g_args)

    test_src = add1.out.make_source()
    with test_src as src:
        assert_array_equal(6 * np.ones(shape),
                            src.get_frame(0))
