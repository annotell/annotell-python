import re
import numpy as np


def _camel_case_to_snake_case(name):
    # magic
    name = name.replace('__', '')
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _convert_json_camel_2_snake(camel_case_dict):
    return dict((_camel_case_to_snake_case(key), value) for (key, value) in camel_case_dict.items())


class Constants:
    """
    useful constants instead of using a string -> easier to change later
    """
    EDGE = 'edge'
    LEFT = 'Left'
    RIGHT = 'Right'
    TOP = 'Top'
    BOTTOM = 'Bottom'
    COORDINATES = 'coords'
    BOUNDARY_POINTS = 'boundaryPoints'
    VISIBLE = 'visible'


class BaseProperties:
    def __init__(self, object_id):
        self.object_id = object_id

    def __repr__(self):
        tmp = 'A object of type %s with properties:' % self.__class__.__name__
        for key, value in self.__dict__.items():
            tmp += '\n\t%s = %s' % (key, value)
        return tmp


class ExtremePoint:
    def __init__(self, coordinate, visible):
        self.coordinate = coordinate
        self.visible = visible
        if type(self.visible) is not bool:
            raise TypeError('visible has to be a boolean')

    def __repr__(self):
        tmp = 'A ExtremePoint'
        tmp += '\n\tcoordinate = [%s, %s]' % tuple(self.coordinate)
        tmp += '\n\tvisible = %s' % self.visible
        return tmp


class BoundingBoxDeleted:
    def __init__(self, properties):
        self.deleted = True
        self.properties = properties

    def __repr__(self):
        return 'A deleted BoundingBox'


class BoundingBox:
    def __init__(self, left_point, right_point, top_point, bottom_point, annotation_type, properties):
        self.deleted = False
        self.left_point = left_point
        self.right_point = right_point
        self.top_point = top_point
        self.bottom_point = bottom_point

        self.annotation_type = annotation_type
        self.properties = properties

    def __repr__(self):
        return 'A BoundingBox of type %s' % self.annotation_type

    @property
    def edge_visibility(self):
        # returns the visibility of left box point, right box point, bottom box point and top box point respectively
        return np.array([self.left_point.visible, self.right_point.visible, self.bottom_point.visible,
                         self.top_point.visible])

    @property
    def box_coordinates(self):
        # returns left box point, right box point, bottom box point and top box point
        return np.array([self.left_point.coordinate[0], self.right_point.coordinate[0], self.bottom_point.coordinate[1],
                         self.top_point.coordinate[1]])

    @property
    def box_position(self):
        # returns vector of position: left, right, bottom, top
        return np.array([self.left_point.coordinate, self.right_point.coordinate, self.bottom_point.coordinate,
                         self.top_point.coordinate])


class BoundingBoxFactory:
    def __init__(self, property_factory):
        self.property_factory = property_factory

    def bounding_box_factory(self, boundaries, annotation_type, properties):
        for i_boundary in boundaries:
            if i_boundary[Constants.EDGE] == Constants.LEFT:
                left_point = ExtremePoint(i_boundary[Constants.COORDINATES], i_boundary[Constants.VISIBLE])
            elif i_boundary[Constants.EDGE] == Constants.RIGHT:
                right_point = ExtremePoint(i_boundary[Constants.COORDINATES], i_boundary[Constants.VISIBLE])
            elif i_boundary[Constants.EDGE] == Constants.TOP:
                top_point = ExtremePoint(i_boundary[Constants.COORDINATES], i_boundary[Constants.VISIBLE])
            elif i_boundary[Constants.EDGE] == Constants.BOTTOM:
                bottom_point = ExtremePoint(i_boundary[Constants.COORDINATES], i_boundary[Constants.VISIBLE])

        properties = self.property_factory(annotation_type, properties)

        return BoundingBox(left_point, right_point, top_point, bottom_point, annotation_type, properties)
