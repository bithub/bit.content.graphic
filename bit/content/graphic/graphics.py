from StringIO import StringIO

import PIL.Image

from persistent.dict import PersistentDict
from zope.interface import alsoProvides, noLongerProvides, implements

from zope.annotation.interfaces import IAnnotations

from plone.namedfile import NamedBlobImage
from plone.namedfile.interfaces import INamedBlobImage

from Products.CMFCore.utils import getToolByName

from p4a.subtyper.interfaces import ISubtyper

from bit.content.graphic.interfaces import\
    ICustomGraphic, IGraphicallyCustomized


ANNOGRAPHICS = 'bit.plone.graphic.Graphical'


class CustomGraphic(object):
    implements(ICustomGraphic)

    def __init__(self, context, *largs, **kwargs):
        self.context = context

    def getImage(self, name=None):
        imagedict = IAnnotations(
            self.context).get('bit.plone.graphic.CustomGraphic')
        if not imagedict:
            return
        image = imagedict.get(name or 'original')
        if not image and name in self._sizes.keys():
            image = self._resize(imagedict.get('original'), name)
            imagedict[name] = image
        return image

    _sizes = {'large': (768, 768),
              'preview': (400, 400),
              'mini': (200, 200),
              'thumb': (128, 128),
              'tile': (64, 64),
              'icon': (32, 32),
              'listing': (16, 16),
         }

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
        return NamedBlobImage(
            thumbnail_file.read(), filename=original.filename)

    def setImage(self, image, contentType=None, filename=None):
        if image and not INamedBlobImage.providedBy(image):
            if hasattr(image, 'data'):
                data = image.data
            elif hasattr(image, 'read'):
                data = image.read()
            else:
                data = image
            if hasattr(image, 'filename') and not filename:
                filename = unicode(image.filename)
            elif hasattr(image, 'name') and not filename:
                filename = image.name.split('/').pop()
            if hasattr(image, 'contentType') and not contentType:
                contentType = image.contentType
            elif hasattr(image, 'encoding') and not contentType:
                contentType = image.encoding
            image = NamedBlobImage(data, contentType, unicode(filename))

        if not image and IGraphicallyCustomized.providedBy(self.context):
            noLongerProvides(self.context, IGraphicallyCustomized)
            del IAnnotations(self.context)['bit.plone.graphic.CustomGraphic']
        if image and not IGraphicallyCustomized.providedBy(self.context):
            alsoProvides(self.context, IGraphicallyCustomized)
        if image:
            IAnnotations(
                self.context)['bit.plone.graphic.CustomGraphic']\
                = PersistentDict()
            IAnnotations(
                self.context).get(
                'bit.plone.graphic.CustomGraphic')['original']\
                = image


class Graphical(object):

    def __init__(self, context):
        self. context = context

    def copyGraphics(self, src):
        for k in src.graphicKeys(expand=False):
            self.setGraphic(k, src.getRawGraphic(k, expand=False))

    def getGraphic(self, graphicid, acquire=False, ctx=None):
        ctx = ctx or self.context
        res = self.getRawGraphic(graphicid)
        if not res and acquire:
            try:
                return self.getGraphic(
                    graphicid, acquire, ctx=ctx.aq_inner.aq_parent)
            except:
                return None
        if not res:
            return None
        base_url = ctx.absolute_url_path()
        if res.startswith('http://'):
            return res
        if res.startswith('/'):
            root = getToolByName(ctx, 'portal_url').getPortalObject()
            res = res[1:]
            path = root.absolute_url_path()
        else:
            path = base_url
        if path.endswith('/'):
            path = path[:-1]
        return res

    def getRawGraphic(self, graphicid, acquire=False, expand=True):
        graphics = IAnnotations(
            self.context).get('bit.plone.graphic.Graphical')
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

    def graphicKeys(self, expand=True):
        anno = IAnnotations(self.context)
        graphics = anno.get(
            'bit.plone.graphic.Graphical')
        keys = set()
        if graphics:
            if 'base' in graphics.keys() and expand:
                [keys.add(k) for k in self._default_sizes]
                [keys.add(k) for k in graphics.keys() if k != 'base']
            else:
                [keys.add(k) for k in graphics.keys()]
        return list(keys)

    def getGraphics(self):
        graphics = {}
        [graphics.__setitem__(x, self.getRawGraphic(x))
         for x in self.graphicKeys(expand=False)]
        return graphics

    def graphicList(self):
        return ['%s:%s' % (x, self.getRawGraphic(x))
                for x in self.graphicKeys()]

    def getRawList(self):
        return ['%s:%s' % (x, self.getRawGraphic(x, expand=False))
                for x in self.graphicKeys(expand=False)]

    def clearGraphics(self):
        anno = IAnnotations(self.context)
        anno['bit.plone.graphic.Graphical'] = {}
        self.context.reindexObject(idxs=['getGraphics'])

    def setGraphic(self, graphic, path=None):
        #        print 'adding graphic %s as %s to %s'
        # %(graphic, path, self.context.virtual_url_path())
        anno = IAnnotations(self.context)
        if not anno.get('bit.plone.graphic.Graphical'):
            anno['bit.plone.graphic.Graphical'] = PersistentDict()
        if path is not None:
            anno['bit.plone.graphic.Graphical'][graphic] = path
        else:
            del anno['bit.plone.graphic.Graphical'][graphic]

        self.context.reindexObject(idxs=['getGraphics'])
