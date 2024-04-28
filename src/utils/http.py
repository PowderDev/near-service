from fastapi.responses import JSONResponse


def http_error(error_content, status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": error_content}
    )
