# Logging and Exception Handling Implementation

## Overview

Centralized logging and custom exception handling have been implemented across all three FastAPI labs. Each lab now has its own `utils` directory with consistent logging and exception handling utilities.

## Architecture

### Centralized Approach
- Each lab has its own `utils/` directory with identical implementations
- This ensures independence while maintaining consistency
- Logs are stored in `logs/` directory within each lab
- Log files are timestamped: `MM_DD_YYYY_HH_MM_SS.log`

## Files Created

### Common Utilities (in each lab)
- `utils/__init__.py` - Package initialization
- `utils/logger.py` - Logging configuration
- `utils/exception.py` - Custom exception class

### Updated Files
- All `main.py` files - Integrated logging and exception handling
- All route files - Added logging to endpoints
- All `Dockerfile` files - Added logs directory creation
- All `.gitignore` files - Added logs exclusion

## Features

### Logger (`utils/logger.py`)
- **Dual Output**: Logs to both file and console
- **Timestamped Files**: Each run creates a new log file
- **Structured Format**: `[ timestamp ] line_number module - level - message`
- **Auto Directory Creation**: Creates `logs/` directory if it doesn't exist

### Custom Exception (`utils/exception.py`)
- **Detailed Error Messages**: Includes file name, line number, and error message
- **Automatic Logging**: Errors are automatically logged
- **Traceback Support**: Extracts traceback information when available
- **FastAPI Integration**: Works with FastAPI exception handlers

## Implementation Details

### Middleware Lab
- Logs rate limit violations
- Logs request processing times
- Logs all endpoint calls
- Exception handling in middleware and routes

### Versioning Lab
- Logs router inclusion
- Logs version endpoint calls (v1 and v2)
- Logs root endpoint calls
- Exception handling in all routes

### Database Lab
- Logs database operations (CRUD)
- Logs session creation/closing
- Logs background task processing
- Exception handling with database rollback
- Transaction-safe error handling

## Usage Examples

### Using Logger
```python
from utils.logger import logger

logger.info("Application started")
logger.warning("Rate limit approaching")
logger.error("Database connection failed")
logger.debug("Debug information")
```

### Using Custom Exception
```python
from utils.exception import CustomException
import sys

try:
    # Some operation
    pass
except Exception as e:
    raise CustomException(f"Operation failed: {str(e)}", sys)
```

### FastAPI Exception Handler
```python
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    logger.error(f"CustomException raised: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": "CustomException"}
    )
```

## Log File Locations

- **Middleware Lab**: `middleware-lab/logs/`
- **Versioning Lab**: `versioning-lab/logs/`
- **Database Lab**: `database-lab/logs/`

## Docker Integration

All Dockerfiles have been updated to:
- Create `logs/` directory with proper permissions
- Copy `utils/` directory into containers
- Ensure logs persist (if volumes are configured)

## Benefits

1. **Consistency**: Same logging format across all labs
2. **Debugging**: Easy to trace issues with detailed logs
3. **Monitoring**: Track application behavior and errors
4. **Production Ready**: Structured logging suitable for production
5. **Error Tracking**: Detailed exception information for debugging

## Log Format

```
[ 2024-01-15 10:30:45 ] 25 main - INFO - Application started
[ 2024-01-15 10:30:46 ] 30 middleware - WARNING - Rate limit exceeded for IP: 192.168.1.1
[ 2024-01-15 10:30:47 ] 45 database - ERROR - Database connection failed
```

## Notes

- Logs are excluded from git via `.gitignore`
- Each application run creates a new timestamped log file
- Console output is also enabled for real-time monitoring
- Exception details include file path and line numbers for easy debugging

