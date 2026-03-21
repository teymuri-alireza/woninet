from utilities.logger import logger_function
import re

# get logger configuration
rootLogger = logger_function()

def validate_ip(ip_to_check: str) -> bool:
    """
    Validates the IP address and checks if every section of the IP is between 1 and 254
    (255 is ignored, since it's used for broadcast.)

    Parameters:
        ip_to_check (str) : The IP address passed to check.
    
    Returns:
        bool : A True or False boolean with the required logs for errors.
    """
    try:
        # check the count of dots
        rootLogger.debug("Checking the count of dots in the IP address...")
        # using re.escape to prevent errors
        if len(re.findall(pattern=re.escape(pattern="."), string=ip_to_check)) != 3:
            rootLogger.error("Failed. IP address is not valid.")
            return False

        # check the range of ip address
        seperate_ip = ip_to_check.split(".")
        rootLogger.debug("Checking if each part of IP address is between 1 and 254...")
        for part in seperate_ip:
            if int(part) < 0 or int(part) > 254:
                rootLogger.error("Failed. IP address is not in a vlid range.")
                return False
        
        rootLogger.debug("IP validated successfully.")
        return True
    
    except ValueError:
        rootLogger.error("Error. Some parts of IP address are not interger!")
        return False
    
    except Exception as e:
        rootLogger.error(f"Error at validate_ip function: {e}")
        return False