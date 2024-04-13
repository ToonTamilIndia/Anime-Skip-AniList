from flask import Flask, jsonify, request  # Added 'request' import
import requests
import re

app = Flask(__name__)

@app.route("/")
def home():
    return "API is up..."

@app.route('/<anime_name>')
def get_anime_details(anime_name):
    try:
        # Extract episode number from anime name
        match = re.search(r'-episode-(\d+)', anime_name)
        if match:
            episode_number = int(match.group(1))
            anime_name = re.sub(r'-episode-\d+', '', anime_name)
        else:
            episode_number = None

        # Make request to search for anime in Jikan API
        jikan_response = requests.get(f'https://api.jikan.moe/v4/anime?q={anime_name}')
        jikan_response.raise_for_status()
        jikan_data = jikan_response.json()

        # Extract MAL ID from the first result
        mal_id = jikan_data['data'][0]['mal_id']

        # Fetch skip times data if episode number is provided
        skip_times_data = None
        if episode_number is not None:
            skip_times_response = requests.get(f'https://api.aniskip.com/v2/skip-times/{mal_id}/{episode_number}?types=op&types=ed&episodeLength=0')
            skip_times_response.raise_for_status()
            skip_times_data = skip_times_response.json()

        return jsonify({
            'mal_id': mal_id,
            'skip_times_data': skip_times_data
        })
    except requests.exceptions.HTTPError as e:
        # Return null if API call results in a 404 Client Error
        return jsonify({
            'error': '404 Client Error',
            'message': str(e)
        }), 404

if __name__ == '__main__':
    app.run(debug=True)
