import asyncio
import base64
from io import BytesIO

import quart
from quart import request, session, redirect, render_template

from database import Session, func
from models import Tokens, user, rustInfo

from api import api_blueprint

from rustplus import *

import hypercorn

socket = None

async def connectBot():
    global socket  # Use the global socket variable
    socket = RustSocket("IP", "PORT", STEAMID, PLAYER_TOKEN)
    await socket.connect()
    await socket.send_team_message("I have connected to rust plus")


web = quart.Quart(__name__)
web.secret_key = "Hiddnen key"
session_instance = Session()

web.register_blueprint(api_blueprint, url_prefix='/api')
botStarted = False

@web.route("/", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        form = await request.form
        usernameForm = form["username"]
        passwordForm = form["password"]
        user_obj = session_instance.query(user).filter_by(name=usernameForm).first()

        if user_obj and user_obj.password == passwordForm:
            session["username"] = usernameForm
            session_instance.close()

            return redirect("/addBot")
        else:
            session_instance.close()
            return "Wrong name or password"
    else:
        return await render_template("index.html")


@web.route("/register", methods=["GET", "POST"])
async def register():
    if request.method == "POST":
        form = await request.form
        name = form["username"]
        password = form["password"]

        max_uid = session_instance.query(func.max(user.uID)).scalar() or 0
        usr = user(uID=max_uid + 1, name=name, password=password)
        session_instance.add(usr)
        session_instance.commit()

        return redirect("/")

    return await render_template("register.html")


@web.route("/server", methods=["GET", "POST"])
async def server():
    if "username" not in session:
        return redirect("/")
    
    rustInfo = await socket.get_info()
    map = await socket.get_map(False, False, False)
    image_buffer = BytesIO()
    map.save(image_buffer, format='PNG')
    image_data = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
    html_code = f'<img src="data:image/png;base64,{image_data}" class="img-small">'

    safe_html_code = quart.Markup(html_code)
    name = rustInfo.name
    players = rustInfo.players
    maxPlayers = rustInfo.max_players
    size = rustInfo.size
    time = await socket.get_time()


    return await render_template(
        "server.html",
        name=name,
        players=players,
        maxPlayers=maxPlayers,
        map=safe_html_code,
        size=size
    )

@web.route("/bot", methods=["GET", "POST"])
async def bot():
    if "username" not in session:
        return redirect("/")

    return await render_template("bot.html")


@web.route("/addBot", methods=["GET", "POST"])
async def addBot():
    if "username" not in session:
        return redirect("/")

    if request.method == "POST":
        form = await request.form
        rustToken = form["rustToken"]
        steamID = form["steamID"]
        ip = form["IP"]
        port = form["port"]

        tokens = Tokens(rustToken=rustToken, steamID=steamID, IP=ip, port=port)
        session_instance.add(tokens)
        session_instance.commit()

    return await render_template("addBot.html")


@web.route("/logout", methods=["GET", "POST"])
async def logout():
    if "username" in session:
        session.pop("username", None)
        return redirect("/")
    else:
        return "You were not logged in"
    
async def start_app():
    await asyncio.gather(connectBot())
    config = hypercorn.Config()
    config.bind = ["0.0.0.0:8003"]
    await hypercorn.asyncio.serve(web, config)

if __name__ == "__main__":
    asyncio.run(start_app())