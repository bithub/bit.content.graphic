from zope.interface import Interface as I


class ICustomGraphic(I):

    def getImage():
        pass

    def setImage():
        pass


class IGraphical(I):

    def getGraphic(graphic):
        pass

    def setGraphic(graphic, path):
        pass

    def graphicKeys():
        pass

    def graphicList():
        pass

    def clearGraphics():
        pass

    def getRawGraphic(graphic, path):
        pass


class IGraphicallyCustomized(I):
    pass


class IIconic(I):
    """Allow the getIcon to be adapted
    """

    def getIcon():
        """ return a custom icon
        """
