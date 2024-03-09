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




def generate_email_token():
    code = ''
    for i in range(4):
        code += str(random.randint(0, 9))
    return code
