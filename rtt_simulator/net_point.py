import constants

class NetworkPoint():
    def __init__(self, name, type, city, lat=constants.DEFAULT_LAT_LONG,
                long=constants.DEFAULT_LAT_LONG):
        self.point_name = name
        self.point_type = type
        self.city = city

        if self.point_type == constants.GS_POINT_TYPE:
            self.latitude = lat
            self.longitude = long

    def name(self):
        return self.point_name

    def city(self):
        return self.city

    def location(self):
        if not self.is_extraterrestrial(): 
            raise AttributeError("NetworkPoint of type '" + self.type + \
                                "' has no location attribute")
        return (self.latitude, self.longitude)

    def is_terrestrial(self):
        return self.point_type == constants.GS_POINT_TYPE

    def is_extraterrestrial(self):
        return self.point_type == constants.CITY_POINT_TYPE
