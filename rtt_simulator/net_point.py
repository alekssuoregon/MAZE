import constants

class NetworkPoint():
    def __init__(self, name, type, lat, long):
        self.point_name = name
        self.point_type = type
        self.latitude = lat
        self.longitude = long

    def name(self):
        return self.point_name

    def type(self):
        return self.point_type

    def location(self):
        return (self.latitude, self.longitude)

    def is_terrestrial(self):
        return self.point_type == constants.CITY_POINT_TYPE

    def is_extraterrestrial(self):
        return self.point_type == constants.GS_POINT_TYPE
