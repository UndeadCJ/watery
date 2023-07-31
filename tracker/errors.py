from rest_framework.exceptions import APIException


class BadParams(APIException):
    status_code = 400
    default_detail = "Parâmetro(os) inválidos"
    default_code = "invalid_params"
