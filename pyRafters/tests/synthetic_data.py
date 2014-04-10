from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six

import numpy as np


def random(shape, scale=1, offset=0, seed=0, dtype=np.float):
    """
    Return a deterministic array of random uniformly
    distributed between [offset, offset + scale)

    The random seed is controlled via `seed`

    Parameters
    ----------
    shape : tuple
        shape of the returned array

    scale : float
       range of random numbers

    offset : float
       minimum value of results

    seed : int
       Seed handed to np.random.seed, defaults to 0

    dtype : np.dtype
       type to cast results to via astype
    """
    np.random.seed(seed)
    return (offset + scale * np.random.rand(*shape)).astype(dtype)


def gradient_2D(shape, offset=0, flipud=False,
            fliplf=False, mod_val=None, dtype=None):
    """
    Return a diagonal gradient

    Parameters
    ----------
    shape : len 2 tuple
        dimensions of the output

    offset : scalar
       offset to add to array, applied before mod

    flipud : bool
       If the output should be flipped vertically

    fliplf : bool
       If the output should be flipped horizontally

    mod_val : scalar or None
       If not None, take return mod(array, mod_val)

    dtype : np.dtype or None
       type to cast results to if not None
    """
    tmp = np.ones(shape)
    # integrate image
    tmp = tmp.cumsum(0).cumsum(1) + offset
    if flipud:
        tmp = np.flipud(tmp)

    if fliplf:
        tmp = np.fliplr(tmp)

    if mod_val is not None:
        tmp = np.mod(tmp, mod_val)

    if dtype is not None:
        tmp = tmp.astype(dtype)

    return tmp


def sinsin(shape, k1, k2, dtype=None, scale=128, p1=0, p2=0):
    """
    Generates an image of the form Z = sin(k1 * x) * sin(k2 * y) + 1

    with x, y in [0, 2*np.pi) and sampled at shape points

    Parameters
    ----------
    shape : tuple
       Shape of output image, should be length 2

    k1, k2 : scalar
       Spatial frequency of sin

    dtype : np.dtype or str
       The target data type

    scale : scalar
       Scale factor, there is a rouge factor of 2 from shifting
       the data to be always positive, max value will be 2 * scale

    p1, p2 : scalar
       Phase shift, defaults to 0

    Returns
    -------
    ret : ndarray
        single 2D image
    """
    if dtype is None:
        dtype = np.uint8

    X = np.linspace(0, 2*np.pi, shape[0]).reshape(-1, 1)
    Y = np.linspace(0, 2*np.pi, shape[0]).reshape(1, -1)

    sX = np.sin(k1 * X + p1)
    sY = np.sin(k2 * Y + p2)

    return (scale * (sX * sY + 1)).astype(dtype)
