import math

EARTH_RADIUS = 6378135.0

class ConstellationConfig():
    def __init__(
            self,
            name,
            eccentricity,
            arg_of_preigee_degree,
            phase_diff,
            mean_motion_rev_per_day,
            altitude_m,
            max_gsl_length_m,
            max_isl_length_m,
            num_orbs,
            num_sats_per_orb,
            inclination_degree
        ):
            self.name = name
            self.eccentricity = eccentricity
            self.arg_of_preigee_degree = arg_of_preigee_degree
            self.phase_diff = phase_diff
            self.mean_motion_rev_per_day = mean_motion_rev_per_day
            self.altitude_m = altitude_m
            self.max_gsl_length_m = max_gsl_length_m
            self.max_isl_length_m = max_isl_length_m
            self.num_orbs = num_orbs
            self.num_sats_per_orb = num_sats_per_orb
            self.inclination_degree = inclination_degree

def GetStarlinkConfig():
    eccentricity = 0.0000001
    arg_of_preigee_degree = 0.0
    phase_diff = True
    mean_motion_rev_per_day = 15.19
    altitude_m = 550000
    satellite_cone_radius_m = 940700
    max_gsl_length_m = math.sqrt(math.pow(satellite_cone_radius_m, 2) + math.pow(altitude_m, 2))
    max_isl_length_m = 2 * math.sqrt(math.pow(EARTH_RADIUS + altitude_m, 2) - math.pow(EARTH_RADIUS + 80000, 2))
    num_orbs = 72
    num_sats_per_orb = 22
    inclination_degree = 53

    return ConstellationConfig("Starlink_550", eccentricity, arg_of_preigee_degree, \
            phase_diff, mean_motion_rev_per_day, altitude_m, \
            max_gsl_length_m, max_isl_length_m, num_orbs, num_sats_per_orb, inclination_degree)

def GetKuiperConfig():
    eccentricity = 0.0000001
    arg_of_preigee_degree = 0.0
    phase_diff = True
    mean_motion_rev_per_day = 14.80
    altitude_m = 630000
    satellite_cone_radius_m = altitude_m / math.tan(math.radians(30.0))
    max_gsl_length_m = math.sqrt(math.pow(satellite_cone_radius_m, 2) + math.pow(altitude_m, 2))
    max_isl_length_m = 2 * math.sqrt(math.pow(EARTH_RADIUS + altitude_m, 2) - math.pow(EARTH_RADIUS + 80000, 2))
    num_orbs = 34
    num_sats_per_orb = 34
    inclination_degree = 51.9

    return ConstellationConfig("Kuiper_630", eccentricity, arg_of_preigee_degree, \
            phase_diff, mean_motion_rev_per_day, altitude_m, \
            max_gsl_length_m, max_isl_length_m, num_orbs, num_sats_per_orb, inclination_degree)

def GetTelesatConfig():
    eccentricity = 0.0000001
    arg_of_preigee_degree = 0.0
    phase_diff = True
    mean_motion_rev_per_day = 13.66
    altitude_m = 1015000
    satellite_cone_radius_m = altitude_m / math.tan(math.radians(10.0))
    max_gsl_length_m = math.sqrt(math.pow(satellite_cone_radius_m, 2) + math.pow(altitude_m, 2))
    max_isl_length_m = 2 * math.sqrt(math.pow(EARTH_RADIUS + altitude_m, 2) - math.pow(EARTH_RADIUS + 80000, 2))
    num_orbs = 27
    num_sats_per_orb = 13
    inclination_degree = 98.98

    return ConstellationConfig("Telesat_1015", eccentricity, arg_of_preigee_degree, \
            phase_diff, mean_motion_rev_per_day, altitude_m, \
            max_gsl_length_m, max_isl_length_m, num_orbs, num_sats_per_orb, inclination_degree)
