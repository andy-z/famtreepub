'''
Created on Sep 27, 2012

@author: salnikov
'''

from size import Size

class TextBox(object):
    '''
    classdocs
    '''


    def __init__(self, **kw):
        '''
        Constructor takes these keyword arguments:
            x0: lowest X coordinate of corner (def: 0)
            y0: lowest Y coordinate of corner (def: 0)
            width: width of a box (def: 0)
            height: height of a box (def: 0)
            text: text contained in a box (def: '')
            rect_style: SVG style for rectangle
            text_style: SVG style for text
            line_spacing: space between lines (def: 2pt)
            padding: box padding space (def: 3pt)
        '''
        self._x0 = Size(kw.get('x0', 0))
        self._y0 = Size(kw.get('y0', 0))
        self._width = Size(kw.get('width', 0))
        self._height = Size(kw.get('height', 0))
        self._text = kw.get('text', '')
        
        self._kw = kw.copy()

    @property
    def x0(self): return self._x0

    @property
    def x1(self): return self._x0 + self._width

    @property
    def y0(self): return self._y0

    @property
    def y1(self): return self._y0 + self._height

    @property
    def midx(self): return self._x0 + self._width/2

    @property
    def midy(self): return self._y0 + self._height/2

    @property
    def width(self): return self._width

    @property
    def height(self): return self._height

    @property
    def text(self): return self._text




if __name__ == "__main__":
    
    #
    # Run unit test if run as main script
    #
    import unittest
    
    class TextBoxUnitTest(unittest.TestCase):
    
        def test_1_constr(self):
            
            box = TextBox(x0=Size(1), y0=Size(2), width=Size(4), height=Size(8), text='abc')
            self.assertEqual(box.x0.value, 1)
            self.assertEqual(box.y0.value, 2)
            self.assertEqual(box.width.value, 4)
            self.assertEqual(box.height.value, 8)
            self.assertEqual(box.text, 'abc')
            
        def test_2_dim(self):
            
            box = TextBox(x0=Size(1), y0=Size(2), width=Size(4), height=Size(8))
            self.assertEqual(box.x1.value, 5)
            self.assertEqual(box.y1.value, 10)
            self.assertEqual(box.midx.value, 3)
            self.assertEqual(box.midy.value, 6)
            
            
            
    suite = unittest.TestLoader().loadTestsFromTestCase(TextBoxUnitTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
