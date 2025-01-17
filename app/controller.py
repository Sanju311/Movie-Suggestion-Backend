from flask import Blueprint, request, jsonify
from .service.service import get_movie_recommendations

controller_bp = Blueprint('controller_bp', __name__)

@controller_bp.route('/GetMovieRecommendations/<input_string>', methods=['GET'])
def process_string(input_string):

    pass
    #call main service function
    #return response