"""

A set of base classes to provide the interface between the interface
between the front-end frame work and the back-end tools.

"""
import IPython.utils.traitlets as traitlets


## a set of custom triatlets
class IntRange(traitlets.Int):
    """
    An integer traitlet with a limited range.
    """
    _err_str = ("Value must be between {_min} and {_max}.  " +
                "The value {val} was given.")

    def __init__(self, min_max, **kwargs):
        if min_max is None:
            raise ValueError("min_max must be non-None")
        self._min, self._max = min_max
        traitlets.Int.__init__(self, self._min, **kwargs)

    def validate(self, obj, value):
        # call base validate, either an Int or dead
        value = traitlets.Int.validate(self, obj, value)
        if value < self._min or value > self._max:
            raise traitlets.TraitError(self._err_str.format(
                _min=self._min, _max=self._max, val=value))
        return value


class FilePath(traitlets.Unicode):
    """
    A path to a file.  Currently a no-op class, but
    have plans to be able to validate that a file does/does
    not exist.
    """
    @property
    def filters(self):
        if self.get_metadata('filters'):
            return self.get_metadata('filters')
        return ()


# a map between traitlets and the types used in the json files
_trait_map = {traitlets.Int: 'int',
            traitlets.Float: 'float',
            FilePath: 'file_select'}


def _get_label(key, trait):
    label = trait.get_metadata('label')
    if label:
        return label
    return key


# classes for defining tools
class ToolBase(traitlets.HasTraits):
    """
    Base class for `Tool` objects.

    These are objects that will hold the meta-data about the tool
    (such as input data types, required parameters, output types etc),
    accumulate inputs/parameters, validate the inputs provide tools for
    introspection, and run the tool when called.
    """

    _registry = {}

    @classmethod
    def register(cls, sub_class):
        """

        """
        cls._registry[sub_class.__name__] = sub_class

    @property
    def id(self):
        """
        Return the 'id' of the tool.

        Returns
        -------
        id : str
           The id of the tool
        """
        return self.__class__.__name__.lower()

    @property
    def params(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'param'
        """
        return [(k, v) for k, v in self.traits().items()
                if v.get_metadata('role') == 'param']

    @property
    def input_files(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'input_file'
        """
        return [(k, v) for k, v in self.traits().items()
                if v.get_metadata('role') == 'input_file']

    @property
    def output_files(self):
        """
        Returns a list of (key, value) pairs for the
        traits with the role 'input_file'
        """
        return [(k, v) for k, v in self.traits().items()
                if v.get_metadata('role') == 'output_file']

    def format_json_input(self):
        """
        Returns a dictionary which matches the parsed result of 'input'
        section of the existing json files

        """
        out = []
        # loop over the parameters
        for k, v in self.params:
            # get the ones labeled input
            tmp_dict = {}
            tmp_dict['label'] = _get_label(k, v)
            tmp_dict['type'] = _trait_map[type(v)]
            out.append(tmp_dict)
        # loop over the input files
        for k, v in self.input_files:
            tmp_dict = {}
            tmp_dict['label'] = _get_label(k, v)
            tmp_dict['type'] = _trait_map[type(v)]
            tmp_dict['suffix'] = v.filters[0]
            out.append(tmp_dict)
        # return
        return out

    def format_json_output(self):
        """
        Returns a dictionary which matches the parsed result of 'output'
        section of the existing json files

        """
        out = []
        for k, v in self.output_files:
            tmp_dict = {}
            tmp_dict['name'] = v.get_metadata('name')
            tmp_dict['type'] = v.filters[0]
            out.append(tmp_dict)
        return out

    @property
    def mode(self):
        """
        returns the mode of the tool
        """
        raise NotImplementedError()

    @property
    def title(self):
        """
        Returns the title of the Tool.  Defaults to using the class name.
        """
        return self.__class__.__name__

    @property
    def tutorial(self):
        """
        Return the tutorial, a short description of what the tool is.
        """
        raise NotImplementedError()

    def run(self):
        """
        Runs the tool on the data using the set parameters.  Takes no
        arguments and returns no values.  All non-handled exceptions
        will be raised.
        """
        raise NotImplementedError()

    def gen_json_dict(self):
        """
        Return a dictionary describing the tool to be compatible with
        existing frame work.
        """
        json_dict = {}
        json_dict['id'] = self.id
        json_dict['input'] = self.format_json_input()
        json_dict['output'] = self.format_json_output()
        json_dict['command'] = self.command
        json_dict['mode'] = self.mode
        json_dict['title'] = self.title
        json_dict['tutorial'] = self.tutorial
        return json_dict


class Ptychography(ToolBase):
    # input files
    data_file = FilePath(filters=['npy'],
                         label='Data file',
                         role='input_file')
    obj_config_in = FilePath(filters=['npy'],
                               label='Input Object Config File',
                                role='input_file')
    probe_config_in = FilePath(filters=['npy'],
                                 label='Input Probe config file',
                                 role='input_file')
    # parameters
    scan_number = traitlets.Int(label='Scan number', role='param')
    replicated_number = traitlets.Int(label='Replicated Number',
                                      role='param')
    iterations = traitlets.Int(label='Iterations', role='param')

    # output files
    image = FilePath(filters=['png'],
                     label='image',
                     role='output_file',
                     name='image')
    obj_config_out = FilePath(filters=['npy'],
                               label='Output Object Config File',
                                role='output_file',
                                name='object_config')
    probe_config_out = FilePath(filters=['npy'],
                                 label='Output Probe config file',
                                 role='output_file',
                                 name='probe_config')
    result = FilePath(filters=['zip'],
                      label='result',
                      role='output_file',
                      name='result')

    @property
    def tutorial(self):
        return ("Ptychography is a form of scanning " +
                "diffractive imaging that can successfully " +
                "retrieve the modulus and phase of both the " +
                "sample transmission function and the " +
                "illuminating probe.")

    @property
    def mode(self):
        return 'local'

    @property
    def command(self):
        return "python recon_ptycho_pc.py"

ToolBase.register(Ptychography)
