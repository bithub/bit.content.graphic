from zope.interface import Interface as I


class ICustomGraphic(I):

    def get_image():
        pass

    def set_image():
        pass


class IGraphical(I):

    def get_graphic(graphic):
        pass

    def set_graphic(graphic, path):
        pass

    def graphic_ids():
        pass

    def graphic_list():
        pass

    def clear_graphics():
        pass

    def get_raw_graphic(graphic, path):
        pass

    def get_raw_list():
        pass


class IGraphicallyCustomized(I):
    """ marker interface for objects that store a custom graphic """


class IIconic(I):
    """Allow the getIcon to be adapted
    """

    def get_icon():
        """ return a custom icon
        """
