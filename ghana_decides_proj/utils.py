import random
import string


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generate_random_otp_code():
    code = ''
    for i in range(4):
        code += str(random.randint(0, 9))
    return code


def unique_user_id_generator(instance):
    """
    This is for a django project with a user_id field
    :param instance:
    :return:
    """

    size = random.randint(30,45)
    user_id = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(user_id=user_id).exists()
    if qs_exists:
        return
    return user_id



def unique_region_id_generator(instance):
    """
    This is for a region_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    region_id = "RG-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(R)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(region_id=region_id).exists()
    if qs_exists:
        return None
    return region_id



def unique_constituency_id_generator(instance):
    """
    This is for a constituency_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    constituency_id = "CON-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(C)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(constituency_id=constituency_id).exists()
    if qs_exists:
        return None
    return constituency_id

def unique_zone_id_generator(instance):
    """
    This is for a zone_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    zone_id = "ZN-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(C)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(zone_id=zone_id).exists()
    if qs_exists:
        return None
    return zone_id

def unique_polling_station_id_generator(instance):
    """
    This is for a polling_station_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    polling_station_id = "PS-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(Z)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(polling_station_id=polling_station_id).exists()
    if qs_exists:
        return None
    return polling_station_id



def unique_party_id_generator(instance):
    """
    This is for a party_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    party_id = "PTY-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(P)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(party_id=party_id).exists()
    if qs_exists:
        return None
    return party_id

def unique_parl_can_id_generator(instance):
    """
    This is for a parl_can_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    parl_can_id = "PARL-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(CAN)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(parl_can_id=parl_can_id).exists()
    if qs_exists:
        return None
    return parl_can_id

def unique_prez_can_id_generator(instance):
    """
    This is for a prez_can_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    prez_can_id = "PREZ-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(CAN)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(prez_can_id=prez_can_id).exists()
    if qs_exists:
        return None
    return prez_can_id


def unique_election_id_generator(instance):
    """
    This is for a election_id field
    :param instance:
    :return:
    """
    size = random.randint(5, 7)
    election_id = "ELEC-" + random_string_generator(size=size, chars=string.ascii_uppercase + string.digits) + "-(E)"

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(election_id=election_id).exists()
    if qs_exists:
        return None
    return election_id




def generate_email_token():
    code = ''
    for i in range(4):
        code += str(random.randint(0, 9))
    return code
