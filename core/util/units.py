# -*- coding: utf-8 -*-
"""
This file contains Qudi methods for handling real-world values with units.

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

import numpy as np
import pyqtgraph.functions as fn


def get_unit_prefix_dict():
    """ Return the dictionary, which assigns the prefix of a unit to its
        proper order of magnitude.
    @return dict: keys are string prefix and items are magnitude values.
    """

    unit_prefix_dict = {
        'y': 1e-24,
        'z': 1e-21,
        'a': 1e-18,
        'f': 1e-15,
        'p': 1e-12,
        'n': 1e-9,
        'micro': 1e-6,
        'm': 1e-3,
        '': 1,
        'k': 1e3,
        'M': 1e6,
        'G': 1e9,
        'T': 1e12,
        'P': 1e15,
        'E': 1e18,
        'Z': 1e21,
        'Y': 1e24
        }
    return unit_prefix_dict

def create_formatted_output(param_dict, num_sig_digits=5):
    """ Display a parameter set nicely in SI units.

    @param dict param_dict: dictionary with entries being again dictionaries
                       with two needed keywords 'value' and 'unit' and one
                       optional keyword 'error'. Add the proper items to the
                       specified keywords.
                       Note, that if no error is specified, no proper
                       rounding (and therefore displaying) can be
                       guaranteed.

    @param int num_sig_digits: optional, the number of significant digits will
                               be taken, if the rounding procedure was not
                               successful at all. That will ensure at least that
                               not all the digits are displayed.
                               According to that the error will be displayed.

    @return str: a string, which is nicely formatted.

    Note:  If you want that the values are displayed in a certain order, then
           use OrderedDict from the collections package.
    Note2: The absolute tolerance to a zero is set to 1e-18.

    Example of a param dict:
        param_dict = {'Rabi frequency': {'value':123.43,   'error': 0.321,  'unit': 'Hz'},
                      'ODMR contrast':  {'value':2.563423, 'error': 0.523,  'unit': '%'},
                      'Fidelity':       {'value':0.783,    'error': 0.2222, 'unit': ''}}

        If you want to access on the value of the Fidelity, then you can do
        that via:
            param_dict['Fidelity']['value']
        or on the error of the ODMR contrast:
            param_dict['ODMR contrast']['error']


    """

    output_str = ''
    atol = 1e-18    # absolute tolerance for the detection of zero.

    for entry in param_dict:
        if param_dict[entry].get('error') is not None:

            value, error, digit = round_value_to_error(param_dict[entry]['value'], param_dict[entry]['error'])

            if np.isclose(value, 0.0, atol=atol) or np.isnan(error) or np.isclose(error, 0.0, atol=atol) or np.isinf(error):

                sc_fact, unit_prefix = fn.siScale(param_dict[entry]['value'])
                str_val = '{0:.{1}e}'.format(param_dict[entry]['value'], num_sig_digits-1)
                if np.isnan(np.float(str_val)):
                    value = np.NAN
                elif np.isinf(np.float(str_val)):
                    value = np.inf
                else:
                    value = float('{0:.{1}e}'.format(param_dict[entry]['value'], num_sig_digits-1))

            else:
                # the factor 10 moves the displayed digit by one to the right,
                # so that the values from 100 to 0.1 are displayed within one
                # range, rather then from the value 1000 to 1, which is default.
                sc_fact, unit_prefix = fn.siScale(error*10)


            output_str += '{0}: {1} \u00B1 {2} {3}{4} \n'.format(entry,
                                                                 round(value*sc_fact, num_sig_digits-1),
                                                                 round(error*sc_fact, num_sig_digits-1),
                                                                 unit_prefix,
                                                                 param_dict[entry]['unit'],
                                                                 )

        else:
            output_str += '{0}: '.format(entry) + fn.siFormat(param_dict[entry]['value'],
                                      precision=num_sig_digits,
                                      suffix=param_dict[entry]['unit']) + '\n'


    return output_str


def round_value_to_error(value, error):
    """ The scientifically correct way of rounding a value according to an error.

    @param float or int value: the measurement value
    @param float or int error: the error for that measurement value

    @return tuple(float, float, int):
                float value: the rounded value according to the error
                float error: the rounded error
                int rounding_digit: the digit, to which the rounding
                                    procedure was performed. Note a positive
                                    number indicates the position of the
                                    digit right from the comma, zero means
                                    the first digit left from the comma and
                                    negative numbers are the digits left
                                    from the comma. That is a convention
                                    which is used in the native round method
                                    and the method numpy.round.

    Note1: the input type of value or error will not be changed! If float is
           the input, float will be the output, same applies to integer.

    Note2: This method is not returning strings, since each display method
           might want to display the rounded values in a different way.
           (in exponential representation, in a different magnitude, ect.).

    Note3: This function can handle an invalid error, i.e. if the error is
           zero, NAN or infinite. The absolute tolerance to detect a number as
           zero is set to 1e-18.

    Procedure explanation:
    The scientific way of displaying a measurement result in the presents of
    an error is applied here. It is the following procedure:
        Take the first leading non-zero number in the error value and check,
        whether the number is a digit within 3 to 9. Then the rounding value
        is the specified digit. Otherwise, if first leading digit is 1 or 2
        then the next right digit is the rounding value.
        The error is rounded according to that digit and the same applies
        for the value.

    Example 1:
        x_meas = 2.05650234, delta_x = 0.0634
            => x =  2.06 +- 0.06,   (output: (2.06, 0.06, 2)    )

    Example 2:
        x_meas = 0.34545, delta_x = 0.19145
            => x = 0.35 +- 0.19     (output: (0.35, 0.19, 2)    )

    Example 3:
        x_meas = 239579.23, delta_x = 1289.234
            => x = 239600 +- 1300   (output: (239600.0, 1300.0, -2) )

    Example 4:
        x_meas = 961453, delta_x = 3789
            => x = 961000 +- 4000   (output: (961000, 4000, -3) )

    """

    atol = 1e-18    # absolute tolerance for the detection of zero.

    # check if error is zero, since that is an invalid input!
    if np.isclose(error, 0.0, atol=atol) or np.isnan(error) or np.isinf(error):
        #self.log.error('Cannot round to the error, since either a zero error ')
        #logger.warning('Cannot round to the error, since either a zero error '
        #            'value was passed for the number {0}, or the error is '
        #            'NaN: Error value: {1}. '.format(value, error))

        # set the round digit to float precision
        round_digit = -12

        return value, error, round_digit

    # error can only be positive!
    log_val = np.log10(abs(error))

    if log_val < 0:
        round_digit = -(int(log_val)-1)
    else:
        round_digit = -(int(log_val))

    first_err_digit = '{:e}'.format(error)[0]

    if first_err_digit in ('1', '2'):
        round_digit += 1

    # Use the python round function, since np.round uses the __repr__ conversion
    # function which shows enough digits to unambiguously identify the number.
    # But the __str__ conversion should round the number to a reasonable number
    # of digits, which is the standard output of the python round function.
    # Therefore take the python round function.

    return round(value, round_digit), round(error, round_digit), round_digit


def get_relevant_digit(entry):
    """ By using log10, abs and int operations, the proper relevant digit is
        obtained.

    @param flaot entry:

    @return: int, the leading relevant exponent
    """

    # the log10 can only be calculated of a positive number.
    entry = np.abs(entry)

    if np.log10(entry) >= 0:
        return int(np.log10(entry))
    else:
        # catch the asymmetric behaviour of the log and int operation.
        return int(int(np.abs(np.log10(entry)))+1 + np.log10(entry)) - (int(np.abs(np.log10(entry))) +1)


def get_si_norm(entry):
    """ A rather different way to display the value in SI notation.

    @param float entry: the float number from which normalization factor should
                        be obtained.

    @return: norm_val, normalization
            float norm_val: the value in a normalized representation.
            float normalization: the factor with which to divide the number.
    """
    val = get_relevant_digit(entry)
    fact = int(val/3)
    power = int(3*fact)
    norm = 10**(power)

    return entry/norm, norm

def is_number(test_value):
    """ Check whether passed value is a number

    @return: bool, True if the passed value is a number, otherwise false.
    """
    return is_integer(test_value) or is_float(test_value) or is_complex(test_value)

def is_integer(test_value):
    """ Check all available integer representations.

    @return: bool, True if the passed value is a integer, otherwise false.
    """

    return type(test_value) in [np.int, np.int8, np.int16, np.int32, np.int64,
                                np.uint, np.uint8, np.uint16, np.uint32,
                                np.uint64]

def is_float(test_value):
    """ Check all available float representations.

    @return: bool, True if the passed value is a float, otherwise false.
    """
    return type(test_value) in [np.float, np.float16, np.float32, np.float64]

def is_complex(test_value):
    """ Check all available complex representations.

    @return: bool, True if the passed value is a complex value, otherwise false.
    """

    return type(test_value) in [np.complex, np.complex64, np.complex128]


def in_range(value, lower_limit, upper_limit):
    """ Check if a value is in a given range an return closest possible value in range.
    Also check the range.

    @param value: value to be checked
    @param lower_limit: lowest allowed value
    @param upper_limit: highest allowed value
    @return: value closest to value in range
    """
    if upper_limit > lower_limit:
        u_limit = upper_limit
        l_limit = lower_limit
    else:
        l_limit = upper_limit
        u_limit = lower_limit

    if value > u_limit:
        return upper_limit
    if value < l_limit:
        return lower_limit
    return value
