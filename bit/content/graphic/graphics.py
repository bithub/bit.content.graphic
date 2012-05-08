from StringIO import StringIO

import PIL.Image

from zope.interface import alsoProvides, noLongerProvides, implements

from zope.annotation.interfaces import IAnnotations

from bit.content.graphic.interfaces import\
    ICustomGraphic, IGraphicallyCustomized


class CustomGraphic(object):
    implements(ICustomGraphic)

    _sizes = {'large': (768, 768),
              'preview': (400, 400),
              'mini': (200, 200),
              'thumb': (128, 128),
              'tile': (64, 64),
              'large-icon': (32, 32),
              'icon': (16, 16),
         }

    def __init__(self, context):
        self.context = context

    def set_image(self, name=None):
        if not image and IGraphicallyCustomized.providedBy(self.context):
            noLongerProvides(self.context, IGraphicallyCustomized)
            del IAnnotations(self.context)[self._annotation]
        if image and not IGraphicallyCustomized.providedBy(self.context):
            alsoProvides(self.context, IGraphicallyCustomized)
         if image:
            IAnnotations(
                self.context)[self._annotation] = {}
            IAnnotations(
                self.context).get(
                self._annotation)['original'] = image

    def get_image(self, name=None):
        imagedict = IAnnotations(
            self.context).get(self._annotation)
        if not imagedict:
            return
        image = imagedict.get(name or 'original')
        if not image and name in self._sizes.keys():
            image = self._resize(imagedict.get('original'), name)
            imagedict[name] = image
        return image

    def _resize(self, original, size):
        data = original.data
        original_file = StringIO(data)
        image = PIL.Image.open(original_file)
        original_mode = image.mode
        if original_mode == '1':
            image = image.convert('L')
        elif original_mode == 'P':
            image = image.convert('RGBA')
        size = self._sizes.get(size)
        image.thumbnail(size, PIL.Image.ANTIALIAS)
        format = image.format and image.format or 'PNG'
        if original_mode == 'P' and format == 'GIF':
            image = image.convert('P')
        thumbnail_file = StringIO()
        image.save(thumbnail_file, format, quality=88)
        thumbnail_file.seek(0)
        return thumbnail_file.read()


class Graphical(object):

    _annotation = 'bit.content.graphic.Graphical'

    def __init__(self, context):
        self. context = context

    def get_raw_graphic(self, graphicid, acquire=False, expand=True):
        graphics = IAnnotations(
            self.context).get(self._annotation)
        graphic = None
        if graphics:
            graphic = graphics.get(graphicid) or None
            if not graphic and 'base' in graphics.keys()\
                    and expand and graphicid in self._default_sizes:
                if graphicid != 'original':
                    graphic = '%s_%s' % (graphics.get('base'), graphicid)
                else:
                    graphic = graphics.get('base')
        return graphic and graphic.strip() or None

    _default_sizes = ['mini', 'thumb', 'large', 'preview', 'original', 'tile']

    def graphic_ids(self, expand=True):
        anno = IAnnotations(self.context)
        graphics = anno.get(
            self._annotation)
        keys = set()
        if graphics:
            if 'base' in graphics.keys() and expand:
                [keys.add(k) for k in self._default_sizes]
                [keys.add(k) for k in graphics.keys() if k != 'base']
            else:
                [keys.add(k) for k in graphics.keys()]
        return list(keys)

    def get_graphics(self):
        graphics = {}
        [graphics.__setitem__(x, self.get_raw_graphic(x))
         for x in self.graphic_ids(expand=False)]
        return graphics

    def graphic_list(self):
        return ['%s:%s' % (x, self.get_raw_graphic(x))
                for x in self.graphic_ids()]

    def get_raw_list(self):
        return ['%s:%s' % (x, self.get_raw_graphic(x, expand=False))
                for x in self.graphic_ids(expand=False)]

    def clear_graphics(self):
        anno = IAnnotations(self.context)
        anno[self._annotation] = {}

    def get_graphic(self, graphicid, acquire=False, ctx=None):
        ctx = ctx or self.context
        return self.get_raw_graphic(graphicid)

    def set_graphic(self, graphic, path=None):
        anno = IAnnotations(self.context)
        if not anno.get(self._annotation):
            anno[self._annotation] = PersistentDict()
        if path is not None:
            anno[self._annotation][graphic] = path
        else:
            del anno[self._annotation][graphic]
