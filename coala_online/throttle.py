from rest_framework.throttling import AnonRateThrottle


def throttle(custom_rate):
    """
    Generates a Rate Throttle class
    :param custom_rate: Rate Limiting
    :return: Class with custom rate limiting
    """
    class CustomRateThrottle(AnonRateThrottle):
        rate = custom_rate

    return CustomRateThrottle
