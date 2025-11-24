import sys
import traceback
from typing import Optional
from .logger import logger


class CustomException(Exception):
    """
    Custom exception class to provide detailed error information for FastAPI applications.
    Inherits from the base Exception class.
    """

    def __init__(self, error_message: str, error_detail: Optional[sys] = None):
        """
        Initialize the CustomException with detailed error information.

        Args:
            error_message: The original error message
            error_detail: System information about the error (from sys)
        """
        # Call the parent class (Exception) constructor
        super().__init__(error_message)

        # Get detailed error information
        self.error_message = self._generate_detailed_error_message(error_message, error_detail)

    @staticmethod
    def _generate_detailed_error_message(error_message: str, error_detail: Optional[sys]) -> str:
        """
        Generate a detailed error message including file name, line number, and error description.

        Args:
            error_message: The original error message
            error_detail: System information about the error

        Returns:
            str: Formatted error message with details
        """
        # Get the exception traceback details
        exc_type, exc_obj, exc_tb = sys.exc_info()

        # If we have traceback information, extract details
        if exc_tb is not None:
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno

            # Create detailed error message
            detailed_message = (
                f"\nError occurred in Python script:"
                f"\n→ File: {file_name}"
                f"\n→ Line number: {line_number}"
                f"\n→ Error message: {str(error_message)}"
            )
        else:
            # Fallback if no traceback available
            detailed_message = (
                f"\nError occurred in Python script:"
                f"\n→ Error message: {str(error_message)}"
            )

        # Log the error
        logger.error(detailed_message)

        return detailed_message

    def __str__(self) -> str:
        """
        String representation of the exception.

        Returns:
            str: The detailed error message
        """
        return self.error_message

