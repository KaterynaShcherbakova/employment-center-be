def json_error(msg, code):
    return {'error': {'code': code, 'message' : msg}}, code

class errs:
    not_found = json_error('Not found', 404)
    bad_request = json_error('Invalid request. Bad request body', 400)
    exists = json_error('Forbidden. Already exists', 403)
    no_auth = json_error('Autorisation is not successful', 401)
    no_access = json_error('No access', 403)