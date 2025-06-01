from flask import Blueprint, request, jsonify
from .service.service import get_movie_recomendations

controller_bp = Blueprint('controller_bp', __name__)

@controller_bp.route('/GetMovieRecommendations/<input_string>', methods=['GET'])
def process_string(input_string):
    
    try:

        print("GETTING MOVIE RECOMMENDATIONS...")
        recommendations = get_movie_recomendations(input_string)

        if isinstance(recommendations, dict):
            #invalid username
            if recommendations["error"] == "invalid username":
                return jsonify(recommendations), 400

        # Convert DataFrame to JSON (list of dictionaries)
        recommendations_json = recommendations.to_dict(orient="records")

        return jsonify(recommendations_json), 200 
        #convert to JSON or useful format
    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": str(e)}), 500
    