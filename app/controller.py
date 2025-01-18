from flask import Blueprint, request, jsonify
from .service.service import get_movie_recomendations

controller_bp = Blueprint('controller_bp', __name__)

@controller_bp.route('/GetMovieRecommendations/<input_string>', methods=['GET'])
def process_string(input_string):

    return get_movie_recomendations(input_string), 200    
    #convert to JSON or useful format
    
    