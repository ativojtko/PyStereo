# Coordinate conversions, plane-pole conversions, and vector rotations.


from math import cos, radians, sin, degrees, atan2, sqrt

# konverzia plochy na pól
def plane_to_pole(dip_direction, dip):
    """
    Converts a plane (dip direction, dip) to a pole (trend, plunge).
    """

    trend = (dip_direction + 180.0) % 360.0
    plunge = 90.0 - dip

    return trend, plunge

# konverzia pólu na plochu
def pole_to_plane(trend, plunge):
    """
    Converts a pole (trend, plunge) to a plane (dip direction, dip).
    """

    if plunge < 0:
            trend = (trend + 180.0) % 360.0
            plunge = -plunge
    
    dip_direction = (trend - 180.0) % 360.0
    dip = 90.0 - plunge

    return dip_direction, dip


# funkcia pre konverziu sady merania
def _convert_records(data, source_type, target_type, conversion):
    """
    Converts a list of records from one type to another using the provided conversion function.
    """

    result = []
    for item in data:
        converted = item.copy()
        if item["type"] == source_type:
            azimuth, inclination = conversion(item["azimuth"], item["inclination"])
            converted.update(type=target_type, azimuth=azimuth, inclination=inclination)
        result.append(converted)
    return result


def convert_planes_to_poles(data):
    """
    Converts a list of records from planes to poles.
    """
    return _convert_records(data, "S", "P", plane_to_pole)


def convert_poles_to_planes(data):
    """
    Converts a list of records from poles to planes.
    """
    return _convert_records(data, "P", "S", pole_to_plane)


# konverzia sférických súradníc na karteziánske
# osi: x - sever,y - východ a z - dole
def spherical_to_cartesian(trend, plunge, radius=1.0):
    
    trend_rad = radians(trend)
    plunge_rad = radians(plunge)

    # vektor sa rozložil na zložky x, y, z pomocou pravouhlých trojuholníkov
    # vektor ma predvolnú dĺžku 1 = radius
    x = radius * cos(plunge_rad) * cos(trend_rad)
    y = radius * cos(plunge_rad) * sin(trend_rad)
    z = radius * sin(plunge_rad)

    return x, y, z

# konverzia karteziánske súradníc na sférických
# osi: x - sever,y - východ a z - dole
def cartesian_to_spherical(x, y, z):

    # výpočet dĺžky vektora
    radius = sqrt(x * x + y * y + z * z)
    horizontal_length = sqrt(x * x + y * y)

    if radius == 0:
        raise ValueError("A zero vector has no defined direction.")
    
    # Pre vertikálny vektor použi nulový azimut
    if horizontal_length <= 1e-12 * radius:
        trend = 0.0
    else:
        trend = degrees(atan2(y, x))

        # záporné uhly preveď do rozsahu [0, 360)
        if trend < 0:
            trend += 360

    # do vypoctu sme zaradili premenne z a h (dĺžka priemetu), aby sa funkcia dala aplikovať aj na všeobecny vektor
    plunge = degrees(atan2( z , horizontal_length ) )

    return trend , plunge

# rotácia vektora okolo všeobecnej osi
# vstup: vector (x ,y ,z ); rotation_angle v stupňoch; axis v stupňoch
def rotate(vector, rotation_angle_deg, axis):

    trend, plunge = axis

    v1 = rotate_around_z(vector, - trend) 
    v2 = rotate_around_y(v1, plunge)
    v3 = rotate_around_x(v2, rotation_angle_deg)
    v4 = rotate_around_y(v3, - plunge)
    rotated_vector = rotate_around_z(v4, trend)

    return rotated_vector

def rotate_around_z(vector, rotation_angle_deg):

    x, y, z = vector 
    rotation_angle = radians(rotation_angle_deg)
    cosine = cos(rotation_angle)
    sine = sin(rotation_angle)

    new_x = (x*cosine) - (y*(sine))
    new_y = (x*sine) + (y*cosine)
    new_z = z

    rotated_vector = [new_x, new_y, new_z]

    return rotated_vector

def rotate_around_x(vector, rotation_angle_deg):

    x, y, z = vector 
    rotation_angle = radians(rotation_angle_deg)
    cosine = cos(rotation_angle)
    sine = sin(rotation_angle)

    new_x = x
    new_y =(y*cosine) - (z*(sine))
    new_z = (y*sine) + (z*cosine) 

    rotated_vector = (new_x, new_y, new_z)

    return rotated_vector

def rotate_around_y(vector, rotation_angle_deg):

    x, y, z = vector 
    rotation_angle = radians(rotation_angle_deg)
    cosine = cos(rotation_angle)
    sine = sin(rotation_angle)

    new_x = (x*cosine) + (z*(sine))
    new_y = y
    new_z = -(x*sine) + (z*cosine)

    rotated_vector = (new_x, new_y, new_z)

    return rotated_vector

# rotácia celeho datasetu
def rotate_dataset(dataset, rotation_angle_deg, axis):

    rotated_dataset = [item.copy() for item in dataset]
    
    for item in rotated_dataset:
        trend = item["azimuth"]
        plunge = item["inclination"]

        if item["type"] == "S":
            trend, plunge = plane_to_pole(trend, plunge)

        vector = spherical_to_cartesian(trend, plunge)
        rotated_vector = rotate(vector, rotation_angle_deg, axis)
        trend, plunge = cartesian_to_spherical(*rotated_vector)
        
        if item["type"] == "S":
            trend, plunge = pole_to_plane(trend, plunge)

        item["azimuth"] = trend
        item["inclination"] = plunge

    return rotated_dataset

