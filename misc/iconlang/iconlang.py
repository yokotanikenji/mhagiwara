#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
iconlang.py
iconlang python implementation.
based on the identicon implementation by Shin Adachi <shn@glucose.jp>

"""
# g
# PIL Modules
import Image, ImageDraw, ImagePath, ImageColor

__all__ = ['render_identicon', 'IdenticonRendererBase']

class Matrix2D(list):
    """Matrix for Patch rotation"""
    def __init__(self, initial = [0.] * 9):
        assert isinstance(initial, list) and len(initial)==9
        list.__init__(self, initial)
    
    def clear(self):
        for i in xrange(9):
            self[i] = 0.
    
    def set_identity(self):
        self.clear()
        for i in xrange(3):
            self[i] = 1.
    
    def __str__(self):
        return '[%s]' % ', '.join('%3.2f' % v for v in self)
    
    def __mul__(self, other):
        r = []
        if isinstance(other, Matrix2D):
            for y in xrange(3):
                for x in xrange(3):
                    v = 0.0
                    for i in xrange(3):
                        v += (self[i * 3 + x] * other[y * 3 + i])
                    r.append(v)
        else:
            raise NotImplementedError
        return Matrix2D(r)
    
    def for_PIL(self):
        return self[0:6]
    
    @classmethod
    def translate(kls, x, y):
        return kls([1.0, 0.0, float(x),
                    0.0, 1.0, float(y),
                    0.0, 0.0, 1.0])

    @classmethod
    def scale(kls, x, y):
        return kls([float(x), 0.0, 0.0,
                    0.0, float(y), 0.0,
                    0.0, 0.0, 1.0])

    """
    # need `import math`
    @classmethod
    def rotate(kls, theta, pivot=None):
        c = math.cos(theta)
        s = math.sin(theta)

        matR = kls([c, -s, 0., s, c, 0., 0., 0., 1.])
        if not pivot:
            return matR
        return kls.translate(-pivot[0], -pivot[1]) * matR * kls.translate(*pivot)
    """
    
    @classmethod
    def rotateSquare(kls, theta, pivot=None):
        theta = theta % 4
        c = [1., 0., -1., 0.][theta]
        s = [0., 1., 0., -1.][theta]

        matR = kls([c, -s, 0., s, c, 0., 0., 0., 1.])
        if not pivot:
            return matR
        return kls.translate(-pivot[0], -pivot[1]) * matR * kls.translate(*pivot)


class IdenticonRendererBase(object):
    PATH_SET = []
    
    def __init__(self, code):
        """
        @param code code for icon
        """
        if not isinstance(code, int):
            code = int(code)
        self.code = code
    
    def render(self, size):
        """
        render identicon to PIL.Image
        
        @param size identicon patchsize. (image size is 3 * [size])
        @return PIL.Image
        """
        
        # decode the code
        middle, corner, side, foreColor, backColor, mask = self.decode(self.code)

        # make image        
        image = Image.new("RGB", (size * 3, size * 3))
        draw = ImageDraw.Draw(image)
        
        # fill background
        draw.rectangle((0, 0, image.size[0], image.size[1]), fill=backColor)
        
        kwds = {
            'draw': draw,
            'size': size,
            'foreColor':    foreColor,
            'backColor':    backColor
        }
        # middle patch
        self.drawPatch((1, 1), middle[2], middle[1], middle[0], **kwds)

        # side patch
        kwds['type'] = side[0]
        for i in xrange(4):
            if mask & (1 << i) != 0:   # filter by mask
                pos = [(1, 0), (2, 1), (1, 2), (0, 1)][i]
                self.drawPatch(pos, side[2] + 1 + i, side[1], **kwds)
        
        # corner patch
        kwds['type'] = corner[0]
        for i in xrange(4):
            if mask & (1 << (i+4)) != 0:   # filter by mask
                pos = [(0, 0), (2, 0), (2, 2), (0, 2)][i]
                self.drawPatch(pos, corner[2] + 1 + i, corner[1], **kwds)
        
        return image
                
    def drawPatch(self, pos, turn, invert, type, draw, size, foreColor, backColor):
        """
        @param size patch size
        """
        path = self.PATH_SET[type]
        if not path:
            # blank patch
            invert = not invert
            path = [(0., 0.), (1., 0.), (1., 1.), (0., 1.), (0., 0.)]
        patch = ImagePath.Path(path)
        if invert:
            foreColor, backColor = backColor, foreColor
        
        mat = Matrix2D.rotateSquare(turn, pivot=(0.5, 0.5)) *\
              Matrix2D.translate(*pos) *\
              Matrix2D.scale(size, size)
        
        patch.transform(mat.for_PIL())
        draw.rectangle((pos[0] * size, pos[1] * size, (pos[0]+1) * size, (pos[1]+1) * size), fill=backColor)
        draw.polygon(patch, fill=foreColor, outline=foreColor)

    
    ### virtual functions
    def decode(self, code):
        raise NotImplementedError

class DonRenderer(IdenticonRendererBase):
    """
    Don Park's implementation of identicon
    see : http://www.docuverse.com/blog/donpark/2007/01/19/identicon-updated-and-source-released
    """
    
    PATH_SET = [
        [(0, 0), (4, 0), (4, 4), (0, 4)],   # 0
        [(0, 0), (4, 0), (0, 4)],
        [(2, 0), (4, 4), (0, 4)],
        [(0, 0), (2, 0), (2, 4), (0, 4)],
        [(2, 0), (4, 2), (2, 4), (0, 2)],   # 4
        [(0, 0), (4, 2), (4, 4), (2, 4)],
        [(2, 0), (4, 4), (2, 4), (3, 2), (1, 2), (2, 4), (0, 4)],
        [(0, 0), (4, 2), (2, 4)],
        [(1, 1), (3, 1), (3, 3), (1, 3)],   # 8   
        [(2, 0), (4, 0), (0, 4), (0, 2), (2, 2)],
        [(0, 0), (2, 0), (2, 2), (0, 2)],
        [(0, 2), (4, 2), (2, 4)],
        [(2, 2), (4, 4), (0, 4)],
        [(2, 0), (2, 2), (0, 2)],
        [(0, 0), (2, 0), (0, 2)],
        []                                  # 15
    ]
    MIDDLE_PATCH_SET = [0, 4, 8, 15]
    
    # modify path set
    for idx in xrange(len(PATH_SET)):
        if PATH_SET[idx]:
            p = map(lambda vec: (vec[0] / 4.0, vec[1] / 4.0), PATH_SET[idx])
            PATH_SET[idx] = p + p[:1]
    
    def decode(self, code):
        # decode the code        
        middleType  = self.MIDDLE_PATCH_SET[code & 0x03]
        middleInvert= (code >> 2) & 0x01
        cornerType  = (code >> 3) & 0x0F
        cornerInvert= (code >> 7) & 0x01
        cornerTurn  = (code >> 8) & 0x03
        sideType    = (code >> 10) & 0x0F
        sideInvert  = (code >> 14) & 0x01
        sideTurn    = (code >> 15) & 0x03
        blue        = (code >> 17) & 0x07
        green       = (code >> 20) & 0x07
        red         = (code >> 23) & 0x07

        # newly added for iconlang 
        mask        = (code >> 26) & 0xFF
        
        foreColor = (red << 5, green << 5, blue << 5)
        
        return (middleType, middleInvert, 0),\
               (cornerType, cornerInvert, cornerTurn),\
               (sideType, sideInvert, sideTurn),\
               foreColor, ImageColor.getrgb('white'), mask

def render_identicon(code, size, renderer=None):
    if not renderer:
        renderer = DonRenderer
    return renderer(code).render(size)

def word2code(word):
    """
    given a word, return a int value hash code for it, which can be directly passed to render_identicon()
    """

    # lookup table for char
    CHAR_LOOKUP = {"k":24, "v":12, "w":22, "a":20, "l":9, "b":18, "m":14, "x":11, "y":13, "n":10, "c":4, "z":19, "o":17, "d":8, "$":5, "e":21, "p":6, "f":2, "q":0, "g":27, "r":1, "^":23, "h":15, "s":3, "t":26, "i":25, "j":16, "u":7}

    # total length (bits) of 
    CODE_BITS = 34

    grams = []
    history = []

    for char in ("^"+word+"$"):
        # add 1grams
        if char != '^' and char != '$': grams.append(char)

        # add 2grams
        if len(history) >= 1:
            grams.append(history[-1]+char)

        # add 3grams
        if len(history) >= 2:
            grams.append(history[-2]+history[-1]+char)

        history.append(char)

    
    code = 0
    code = (1 << CODE_BITS)-1
    for i, gram in enumerate(grams):
        val = 0
        for char in gram:
            val *= 28      # alphabet (26) + ^ + $
            val += CHAR_LOOKUP[char]

        mask = 1 << ((val+i) % CODE_BITS)
        code ^= mask
    
    return code

if __name__=='__main__':
    import sys

    # list up the basicwords and batch create the icons for them
    words = [] 
    for line in sys.stdin:
        _cells = line.strip().split('\t')
        words.append(_cells[0])

    for word in words:
        code = word2code(word)
        icon = render_identicon(code, 32)
        icon.save('icons/%s.png' % word)
        print 'saving %s.png, code: %08x' % (word, code)
