import numpy as np
import os.path
import os
import itertools
import copy

from .InternalFunctions import _insert_blank_spaces, _get_str_from_array1d, _get_str_from_multiarray, _get_str_from_array#, _compare_arrays

###################
# DataEntry CLASS #
###################


class DataEntry:
    """Class representing a single constraint.
    """

    def __init__(self, 
                 ndim                   = None,  
                 description            = None,  
                 reference              = None,
                 url                    = None,
                 cosmology              = None,
                 dimensions_descriptors = None,  
                 extracted              = None,
                 imf                    = None,
                 parent_field           = None,
                 axes                   = None,  
                 values                 = None,  
                 err_up                 = None,  
                 err_down               = None,  
                 upper_lim              = None,  
                 lower_lim              = None,
                 extra_data             = None ):
        """construct method
        """
        self.ndim                   = ndim                  
        self.description            = description           
        self.reference              = reference             
        self.url                    = url      
        self.cosmology              = cosmology
        self.dimensions_descriptors = dimensions_descriptors
        self.extracted              = extracted
        self.imf                    = imf             
        self.parent_field           = parent_field
        self.axes                   = axes                  
        self.values                 = values                
        self.err_up                 = err_up                
        self.err_down               = err_down              
        self.upper_lim              = upper_lim             
        self.lower_lim              = lower_lim             
        self.extra_data = []
        if extra_data is not None:
            for k in extra_data.keys():
                setattr(self, k, extra_data[k])
                self.extra_data.append(k)
        self.extra_data = np.array(self.extra_data)

    def __repr__(self):
        """string describing the class
        """
        return "corecon DataEntry class"

    def __str__(self):
        """output of print
        """

        ostr=""
        ostr +=                       "ndim                   = %i\n"%self.ndim                  
        ostr +=                       "description            = %s\n"%_insert_blank_spaces(self.description, 25)
        ostr +=                       "reference              = %s\n"%self.reference             
        ostr +=                       "url                    = %s\n"%self.url                   
        ostr +=                       "extracted              = %s\n"%self.extracted              
        ostr +=                       "imf                    = %s\n"%self.imf                    
        ostr +=                       "parent_field           = %s\n"%self.parent_field            
        ostr += _get_str_from_array1d("dimensions_descriptors = ", self.dimensions_descriptors)
        ostr += _get_str_from_array  ("axes                   = ", self.axes     )
        ostr += _get_str_from_array1d("values                 = ", self.values   )
        ostr += _get_str_from_array1d("err_up                 = ", self.err_up   )
        ostr += _get_str_from_array1d("err_down               = ", self.err_down )
        ostr += _get_str_from_array1d("upper_lim              = ", self.upper_lim)
        ostr += _get_str_from_array1d("lower_lim              = ", self.lower_lim)
        for ed in self.extra_data:
            ostr += _get_str_from_array1d(ed+" "*max(0,23-len(ed))+"= ", getattr(self, ed) )
        return ostr

    def __eq__(self,other):
        """custom equality definition
        """

        #need to check extra_fields here
        if len(self.extra_data) != len(other.extra_data):
            return False
        else:
            for s,o in zip(self.extra_data, other.extra_data):
                if (s != o) or ( np.any(getattr(self,s) != getattr(other,o)) ):
                    return False
            #all ok for extra_data, now check the rest
            return(
                               (self.ndim                   == other.ndim                                     ) & \
                               (self.description            == other.description                              ) & \
                               (self.reference              == other.reference                                ) & \
                               (self.url                    == other.url                                      ) & \
                               (self.extracted              == other.extracted                                ) & \
                               (self.imf                    == other.imf                                      ) & \
                               (self.parent_field           == other.parent_field                             ) & \
                    np.all     (self.dimensions_descriptors == other.dimensions_descriptors                   ) & \
                    np.all     (self.axes                   == other.axes                                     ) & \
                    np.allclose(self.values                 ,  other.values                 , equal_nan=True  ) & \
                    np.allclose(self.err_up                 ,  other.err_up                 , equal_nan=True  ) & \
                    np.allclose(self.err_down               ,  other.err_down               , equal_nan=True  ) & \
                    np.all     (self.upper_lim              == other.upper_lim                                ) & \
                    np.all     (self.lower_lim              == other.lower_lim                                ) )

    def swap_limits(self):
        """Swap upper and lower limits. Useful when computing a derived quantity.
        """
        ul_copy = copy.deepcopy(self.upper_lim)
        self.upper_lim = copy.deepcopy(self.lower_lim)
        self.lower_lim = copy.deepcopy(ul_copy)

    def swap_errors(self):
        """Swap upper and lower errors. Useful when computing a derived quantity.
        """
        eu_copy = copy.deepcopy(self.err_up)
        self.err_up   = copy.deepcopy(self.err_down)
        self.err_down = copy.deepcopy(eu_copy)

    #def none_to_value(self, value):
    #    for f in [self.values, self.err_up, self.err_down]:
    #        w = (f == None)
    #        f[w] = value

    #def none_to_nan(self):
    #    self.none_to_value(np.nan)
    
    def nan_to_values(self, array, new_vals):
        """Replaces all NaN with values.

        :param array: (list of) variable name(s) to work on. Use 'all' to replace NaNs in all array variables.
        :type array: (list of) str
        :param new_vals: value(s) to replace the NaNs with. If a np.array, it should have the correct dimension, i.e. the same as the number of NaNs.
        :type new_vals: float or np.array
        """
        #if array=='values' or array=='all':
        #    w = np.isnan(self.values)
        #    self.values[w] = new_vals
        #if array=='err_up' or array=='all':
        #    w = np.isnan(self.err_up)
        #    self.err_up[w] = new_vals
        #if array=='err_down' or array=='all':
        #    w = np.isnan(self.err_down)
        #    self.err_down[w] = new_vals
        if isinstance(array, str):
            if array=='all':
                names = []
                names.append('values')
                names.append('err_up')
                names.append('err_down')
                for k in self.extra_data:
                    if isinstance(getattr(self,k), np.ndarray):
                        names.append(k)
            else:
                names = [array]
        elif (isinstance(array, list) or isinstance(array, tuple)):
            names = array
        else:
            print("ERROR: the argument 'array' should be a string or a list/tuple of strings!")
            return

        for name in names:
            v = getattr(self, name)
            v[np.isnan(v)] = new_vals
            setattr(self, name, v)

    def set_lim_errors(self, newval, frac_of_values=False):
        """Set the value of error arrays for upper and lower limits.

        :param newval: value to assign to the error arrays.
        :type newval: float
        :param frac_of_values: if True, newval \*= values.
        :type frac_of_values: bool, optional
        """
        w = (self.upper_lim|self.lower_lim)
        if frac_of_values:
            newval *= self.values[w]
        self.err_up   [w] = newval
        self.err_down [w] = newval

    def convert_to_cosmology(self, target_cosmology):
        """Convert from the current to a target cosmology. 
        :param target_cosmology: target cosmology
        :type target_cosmology: astropy.cosmology
        """
        raise NotImplementedError


    def convert_to_IMF(self, target_IMF):
        """Convert from the current to a target IMF. 
        :param target_IMF: target IMF
        :type target_IMF: string
        """
        raise NotImplementedError

        
        if self.imf is None:
            raise AttributeError("IMF is not defined for this entry!")

        assert (target_IMF in ['Salpeter', 'Chabrier', 'Kroupa'])

        # from Speagle et al. 2014 (https://iopscience.iop.org/article/10.1088/0067-0049/214/2/15/pdf)
        stellar_mass_conversion_constants = {'Salpeter' : 0.62, 
                                             'Chabrier' : 1.06, 
                                             'Kroupa'   : 1.0}
        
        if target_IMF != self.imf:
            #compute factors
            this_Mstar_factor = stellar_mass_conversion_constants[self.imf] / stellar_mass_conversion_constants[target_IMF]
            this_Mstar_values_scaling = Mstar_values_scaling[self.parent_field]
            this_Mstar_axes_scaling   = Mstar_axes_scaling[self.parent_field]

            #scale the values
            self.values *= this_Mstar_factor**this_Mstar_values_scaling
            for d in range(self.ndim):
                self.axes[:,d] *= this_Mstar_factor**this_Mstar_axes_scaling[d]
