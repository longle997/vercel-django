import re

class ValidationService():

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate the email format using regex.
        Returns True if valid, False otherwise.
        """
        pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$"
        return re.match(pattern, email) is not None
