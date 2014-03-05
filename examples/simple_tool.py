import numpy as np
import pyLightRafters as plr

# create data
vals, edges = np.histogram(np.random.randn(50000), 50)

# create data sink (numpy based)
d_out = plr.handlers.np_handler.np_dist_sink()
# create data source (numpy based)
d_in = plr.handlers.np_handler.np_dist_source(edges, vals)

# create the tool object
tool = plr.tools.examples.NormalizeDist()

# assign the input and output handlers
tool.output_dist = d_out
tool.input_dist = d_in

# set the parameter
tool.norm_val = 100

# run the tool
tool.run()

# print out the result
print tool.norm_val, np.sum(d_out._vals)
