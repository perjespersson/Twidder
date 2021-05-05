from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import sys
import json

import database_helper
import logic

app = Flask(__name__)
app.debug = True


'''
Default routes that returns static files
'''
@app.route('/')
def index():
    return app.send_static_file('client.html')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('images/favicon.ico')



'''
The "sign up" (POST) route: Handles creating a user

Reciving:
All data is recived via the body of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    if 'email' in data and \
        'password' in data and \
        'firstname' in data and \
        'familyname' in data and \
        'gender' in data and \
        'city' in data and \
        'country' in data:
        if len(data['password']) >= 8:
            
            result = database_helper.create_user(data['email'], data['firstname'], data['familyname'], data['password'], data['gender'], data['city'], data['country'])
            if result['pass']:
                logic.update_sockets({"type" : "stats", "TotalNumUsers" : database_helper.users_total_stats()})
                return jsonify(result), 201 # Code: Created
            else:
                return jsonify(result), 500 # Internal Serever Error
        else:
            return jsonify({'pass': False, "message": "Password needs to be longer."}), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request



'''
The "sign in" (POST) route: Handles signing in a user

Reciving:
All data is recived via the body of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/sign_in', methods=['POST'])
def sign_in():
    data = request.get_json()
    if 'email' in data and \
        'password' in data:
        if (len(data['password']) >= 8):
            result = logic.sign_in(data)
            if result['pass']:
                return jsonify(result), 202 # Accepted
            else:
                return jsonify(result), 400 # Code: Bad request
        else:
            return jsonify({'pass': False, "message": "Password is to short"})
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request



'''
The "sign out" (DELETE) route: Handles signing out a user

Reciving:
All data (the token) is recived via the header of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/sign_out', methods=['DELETE'])
def sign_out():
    token = request.headers['token']
    if token:
        result = database_helper.remove_user(token)
        return jsonify(result)
        if result['pass']:
            logic.remove_socket(token)
            return jsonify(result), 202 # Accepted
        else:
            return jsonify(result), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request



'''
The "change password" (PUT) route: Changes the password of a specific user

Reciving:
The token is recived via the header of the request
All other data is recived via the body of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/change_password', methods=['PUT'])
def change_password():
    data = request.get_json()
    token = request.headers['token']
    if token and \
        'oldpassword' in data and \
        'newpassword' in data:
        if (data['oldpassword'] != data['newpassword']):
            if (len(data['newpassword']) >= 8):
                result = logic.change_password(token, data)
                if result['pass']:
                    return jsonify(result), 202 # Accepted
                else:
                    return jsonify(result), 400 # Code: Bad request
            else:
                return jsonify({'pass': False, "message": "New password to short"})
        else:
            return jsonify({'pass': False, "message": "Old password is the same as new password"}), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request



'''
The "get user data by token" (GET) route: From a users token retrieves and returns its stored information

Reciving:
All data (the token) is recived via the header of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/get_user_data_by_token', methods=['GET'])
def get_user_data_by_token():
    token = request.headers['token']
    if token:
        result = database_helper.get_user_data_by_token(token)
        if result['pass']:
            return jsonify(result), 202 # Accepted
        else:
            return jsonify(result), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request



'''
The "get user data by email" (GET) route: From a users email retrieves and returns its stored information

Reciving:
All data (the email) is recived via the body of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/get_user_data_by_email', methods=['GET'])
def get_user_data_by_email():
    email = request.args.get("email")
    if email:
        result = database_helper.get_user_data_by_email(email)
        if result['pass']:
            return jsonify(result), 202 # Accepted
        else:
            return jsonify(result), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request



'''
The "get user messages by token" (GET) route: From a users token retrieves and returns its received messages

Reciving:
All data (the token) is recived via the header of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/get_user_messages_by_token', methods=['GET'])
def get_user_messages_by_token():
    token = request.headers['token']
    if token:
        result = database_helper.get_user_messages_by_token(token)
        if result['pass']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request



'''
The "get user messages by email" (GET) route: From a users email retrieves and returns its received messages

Reciving:
All data (the email) is recived via the body of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/get_user_messages_by_email', methods=['GET'])
def get_user_messages_by_email():
    token = request.headers['token']
    email = request.args.get("email")
    if email and token:
        result = database_helper.get_user_messages_by_email(token, email)
        if result['pass']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request
    pass



'''
The "post message" (POST) route: It posts a message fron one user to another

Reciving:
The token is recived via the header of the request
All other data is recived via the body of the request

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/post_message', methods=['POST'])
def post_message():
    data = request.get_json()
    token = request.headers['token']
    if 'email' in data and \
        'message' in data and \
        'latitude' in data and \
        'longitude' in data and \
            token:
        result = logic.create_post(token, data['message'], data['email'], data['latitude'], data['longitude'])
        if result['pass']:
            logic.update_sockets({"type" : "stats", "TotalNumPosts" : database_helper.posts_stats()})
            return jsonify(result), 200
        else:
            return jsonify(result), 400 # Code: Bad request
    return jsonify({'pass': False, "message": "Not all data was sent."}), 400 # Code: Bad request


'''
The "socket" route: It sets up and hendles the websockets on serverside.

Return:
Returns both a json object containing information and/or a message, and 
an http-status code.
'''
@app.route('/socket')
def websocket_app():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        while True:
            m = ws.receive()
            if(m):
                message = json.loads(m)
                if (('token' in message) and (message['token'] not in database_helper.signed_in_users)):
                    logic.add_socket_connection(message['token'], ws)
                    logic.update_sockets({"type" : "stats", "TotalNumPosts" : database_helper.posts_stats()})
                    logic.update_sockets({"type" : "stats", "TotalNumUsers" : database_helper.users_total_stats()})
                else:
                    ws.send(json.dumps({'type' : "message", "message" : "Dont know how to handle that"}))
            else:
                # Remove socket from list if its detected as dead
                for key, value in database_helper.signed_in_users.items():
                    if value["socket"] == ws:
                        del database_helper.signed_in_users[key]
                        break
                break
    return jsonify({'pass': True, "message": "Socket dead"}), 200







'''
Server setup and teardown, handles opening and closing both the database and server
'''
@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()


if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()


"""
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
"""