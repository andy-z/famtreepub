'''
Module which defines class for manipulating size values.

Created on Sep 26, 2012

@author: salnikov
'''

import types

class Size(object):
    '''
    Class for specifying size values.
    
    Size can be specified as a number with units, supported units are pt (points),
    in (inches), cm (centimeters), and mm(millimeters). If units are not specified 
    then inches are assumed.    
    '''

    def __init__(self, value = 0):
        '''
        Constructor converts input value to a size.
        
        If input value has numeric type then it is assumed to be size in inches.
        If input value is a string then it should be a floating number followed 
        by optional suffix (one of pt, in, mm, cm). Fithout suffix the number gives
        size in inches.
        
        If string does not have correct format then ValueError is raised. 
        If input value has unsupported type TypeError is raised.
        '''

        if type(value) in [types.FloatType, types.IntType, types.LongType]:
            self.value = float(value)
        elif type(value) in types.StringTypes:
            # convert units to inches
            if value.endswith('pt'):
                self.value = float(value[:-2])/12.
            elif value.endswith('in'):
                self.value = float(value[:-2])
            elif value.endswith('cm'):
                self.value = float(value[:-2])/2.54
            elif value.endswith('mm'):
                self.value = float(value[:-2])/25.4
            else:
                # without suffix assume it's inches
                self.value = float(value)
        elif isinstance(value, Size):
            self.value = value.value
        else:
            raise TypeError("incorrect type of the argument: " + str(type(value)))
        
    def pt(self):
        ''' return size in points ''' 
        return self.value*12.

    def inches(self):
        ''' return size in inches ''' 
        return self.value

    def __str__(self):
        ''' Returns string representation, e.g. "12pt" '''
        return str(self.value*12)+'pt'

    def __sub__(self, other):
        ''' Subtract size from other size '''
        return Size(self.value-other.value)
    
    def __add__(self, other):
        ''' Add two sizes '''
        return Size(self.value+other.value)

    def __mul__(self, other):
        ''' Multiply size by a factor '''
        return Size(self.value*other)

    def __div__(self, other):
        ''' Divide size by a factor '''
        return Size(self.value/other)

    def __rmul__(self, other):
        ''' Multiply size by a factor '''
        return Size(self.value*other)


if __name__ == "__main__":
    
    #
    # Run unit test if run as main script
    #
    import unittest
    
    class SizeUnitTest(unittest.TestCase):
    
        def test_1_val(self):
            
            self.assertEqual(Size().value, 0.)
            self.assertEqual(Size(1).value, 1.)
            self.assertEqual(Size(1L).value, 1.)
            self.assertEqual(Size(1.).value, 1.)
            
        def test_2_str(self):
            self.assertEqual(Size("1").value, 1.)
            self.assertEqual(Size("0.01").value, 0.01)
            self.assertEqual(Size("100").value, 100.)

            self.assertEqual(Size("12pt").value, 1.)
            self.assertEqual(Size("6.6pt").value, 6.6/12)
            self.assertEqual(Size("2.54cm").value, 1)
            self.assertEqual(Size("2.54mm").value, 0.1)
        
            self.assertRaises(TypeError, Size, ([]))

            self.assertRaises(ValueError, Size, ('12px'))
    
        def test_3_arith(self):
    
            s1 = Size("24pt")
            s2 = Size("12pt")

            s3 = s1 + s2
            self.assertEqual(s3.value, 3.)
            s3 = s1 - s2
            self.assertEqual(s3.value, 1.)
            s3 = s1 * 3
            self.assertEqual(s3.value, 6.)
            s3 = 3 * s1
            self.assertEqual(s3.value, 6.)
            s3 = s1 / 4
            self.assertEqual(s3.value, 0.5)
            
        def test_4_meth(self):
            
            s1 = Size("24pt")
            self.assertEqual(s1.pt(), 24)
            self.assertEqual(s1.inches(), 2)
    
        def test_5_copy(self):
            
            s1 = Size("24pt")
            s2 = Size(s1 * 2)
            self.assertEqual(s2.value, 4)
            
        def test_6_str(self):
            
            self.assertEqual(str(Size()), "0.0pt")
            self.assertEqual(str(Size(2)), "24.0pt")
            self.assertEqual(str(Size("1.5in")), "18.0pt")
            
    suite = unittest.TestLoader().loadTestsFromTestCase(SizeUnitTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
