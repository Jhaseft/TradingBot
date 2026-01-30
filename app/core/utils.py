def success(data):
    return {"success": True, "data": data}

def error(message):
    return {"success": False, "error": message}
