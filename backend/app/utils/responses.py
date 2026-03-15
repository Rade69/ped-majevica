"""
Utility funkcije za standardizovane API response-e.
"""
from flask import jsonify


def success_response(data=None, message="Uspešno", status_code=200):
    """
    Standardizovani response za uspešne operacije.
    
    Args:
        data: Podaci koje vraćamo (dict, list, ili None)
        message: Poruka uspeha (string)
        status_code: HTTP status code (default: 200)
    
    Returns:
        Tuple (jsonify response, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'data': data if data is not None else {}
    }
    return jsonify(response), status_code


def error_response(message, status_code=400, errors=None):
    """
    Standardizovani response za greške.
    
    Args:
        message: Glavna poruka greške (string)
        status_code: HTTP status code (default: 400)
        errors: Dodatni detalji o grešci (dict, optional)
    
    Returns:
        Tuple (jsonify response, status_code)
    """
    response = {
        'success': False,
        'message': message,
        'error': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code


def validation_error_response(field_errors):
    """
    Specijalizovani response za validacione greške.
    
    Args:
        field_errors: Dictionary sa greškama po poljima
    
    Returns:
        Tuple (jsonify response, status_code=400)
    """
    return error_response(
        message='Greška u validaciji podataka',
        status_code=400,
        errors=field_errors
    )
