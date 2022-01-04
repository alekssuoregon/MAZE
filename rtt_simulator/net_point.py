import constants

class NetworkPoint():
    """
    NetworkPoint describes a node that is a part of the simulation network

    :param str name: The identifier of the node
    :param str type: The type of node. Either constants.CITY_POINT_TYPE or
        constants.GS_POINT_TYPE
    :param float lat: Latitude of the node
    :param float long: Longitude of the node
    """
    def __init__(self, name, type, lat, long):
        self.point_name = name
        self.point_type = type
        self.latitude = lat
        self.longitude = long

    def name(self):
        """
        :return: The point identifier
        """
        return self.point_name

    def type(self):
        """
        :return: The point type
        """
        return self.point_type

    def location(self):
        """
        :return: The latitude and longitude of the node as a tuple
        """
        return (self.latitude, self.longitude)

    def is_terrestrial(self):
        """
        :return: True if the node is not a ground station communicating with
            the satellite constellation. False otherwise
        """
        return self.point_type == constants.CITY_POINT_TYPE

    def is_extraterrestrial(self):
        """
        :return: True if the node is a ground station communicating with
            the satellite constellation. False otherwise
        """
        return self.point_type == constants.GS_POINT_TYPE
