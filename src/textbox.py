'''
Created on Sep 27, 2012

@author: salnikov
'''

from pysvg import shape, text

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
            font_size: font size (def: 10pt)
            rect_style: SVG style for rectangle
            text_style: SVG style for text
            line_spacing: space between lines (def: 3pt)
            padding: box padding space (def: 3pt)
        '''
        self._x0 = Size(kw.get('x0', 0))
        self._y0 = Size(kw.get('y0', 0))
        self._width = Size(kw.get('width', 0))
        self._height = Size(kw.get('height', 0))
        self._text = kw.get('text', '')
        self._lines = self._text.split('\n')
        self._font_size = Size(kw.get('font_size', '10pt'))
        self._padding = Size(kw.get('padding', '3pt'))
        self._line_spacing = Size(kw.get('line_spacing', '3pt'))
        self._rect_style = kw.get('rect_style', '')
        self._text_style = kw.get('text_style', '')

        # calculate height if needed
        if kw.get('height') is None: self.reflow()

    def _getx0(self): return self._x0
    def _setx0(self, x): self._x0 = x
    x0 = property(_getx0, _setx0)

    @property
    def x1(self): return self._x0 + self._width

    def _gety0(self): return self._y0
    def _sety0(self, y): self._y0 = y
    y0 = property(_gety0, _sety0)

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
    
    def reflow(self):
        '''
        Split the text inside the box so that it fits into box width, then recalculate 
        box height so that all text fits inside the box.
        '''
        self._lines = self._splitText(self._text)
        nlines = len(self._lines)
        self._height = nlines * self._font_size + (nlines-1) * self._line_spacing +  2 * self._padding

    def move(self, x0, y0):
        ''' Sets new coordinates fo x0 nad y0 '''
        self._x0 = Size(x0)
        self._y0 = Size(y0)


    def svg(self):
        ''' Produces list of SVG elements (pysvg obejcts) '''
        
        # render box
        kw = dict(x=str(self.x0), y=str(self.y0), width=str(self.width), height=str(self.height))
        if self._rect_style: kw['style'] = self._rect_style
        rect = shape.rect(**kw)
        
        # render text
        kw = dict(text_anchor='middle')
        if self._text_style: kw['style'] = self._text_style
        txt = text.text(**kw)
        for i, line in enumerate(self._lines):
            x = self.midx
            y = self.y0 + self._padding + self._font_size*(i+1) + self._line_spacing*i
            tspan = text.tspan(x=str(x), y=str(y))
            tspan.appendTextContent(line.encode('utf_8'))
            txt.addElement(tspan)

        return [rect, txt]

    def _splitText(self, text):
        ''' 
        Tries to split a line of text into a number of lines which fit into box width.
        It honors embedded newlines, line will always be split at those first.
        '''
        
        width = self._width - 2*self._padding
        
        lines = [] 
        for line in text.split('\n'):
            words0 = line.split()
            words = words0[:]
            idx = 0
            while idx+1 < len(words):
                twowords = words[idx] + ' ' + words[idx+1]
                if self._textWidth(twowords) <= width:
                    words[idx] = twowords
                    del words[idx+1]
                else:
                    idx += 1
            lines += words
            
        return lines
            

    def _textWidth(self, text):
        ''' Calculates approximate width of the string of text '''
        
        # just  a wild guess for now, try to do better later
        return self._font_size * len(text)


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
            
        def test_3_split(self):
            
            box = TextBox(width='36pt', font_size='10pt')
            lines = box._splitText('abcdefg')
            self.assertEqual(lines, ['abcdefg'])
            lines = box._splitText('abcdefg ABCDEFG')
            self.assertEqual(lines, ['abcdefg', 'ABCDEFG'])
            lines = box._splitText('abcdefg     ABCDEFG')
            self.assertEqual(lines, ['abcdefg', 'ABCDEFG'])
            lines = box._splitText('abc defg   ABCD EFG')
            self.assertEqual(lines, ['abc', 'defg', 'ABCD', 'EFG'])
            
        def test_4_reflow(self):
            
            box = TextBox(width='36pt', text='abcdefg ABCDEFG', font_size='10pt', line_spacing='3pt', padding='5pt')
            box.reflow()
            self.assertEqual(box.height.pt, 10*2 + 3 + 2*5)
            
    suite = unittest.TestLoader().loadTestsFromTestCase(TextBoxUnitTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
