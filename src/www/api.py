"""
    Important, please read:

    The REST API for this bot it not yet functional and will be worked on in the future when this app will be deployed. 
"""

from quart import render_template, Blueprint, jsonify, Quart, request
from database import Session
from models import Tokens, rustInfo

session_instance = Session()
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/Tokens')
def getTokens():
    session_instance = Session()  

    user_obj = session_instance.query(Tokens).filter_by().first()
    session_instance.close()

    if user_obj is None:
        return {'error': 'Data not yet ready'}
    else:
        if user_obj:
            user_data = {
                "rustToken": user_obj.rustToken,
                "steamID": user_obj.steamID,
                "IP": user_obj.IP,
                "port": user_obj.port
            }
            return jsonify(user_data)
        
@api_blueprint.route("/rustPost")
def rustPost():
    rustPost = request.json

    map = rustPost.get('map')
    name = rustPost.get('name')
    players = rustPost.get('players')
    maxPlayers = rustPost.get('maxPlayers')
    size = rustPost.get('size')


    RustInfo = rustInfo(map=map, name=name, players=players, maxPlayers=maxPlayers, size=size)
    session_instance.add(RustInfo)
    session_instance.commit()