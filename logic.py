import secrets
import sys
import json
import requests

import database_helper



'''
Creates a post in the database and getting the location from grocode.xyz 

Parameters:
token: [A token]
message: a string containing the message
email: a string containing the email of the reciver
lat: a float containing the latitude
long: a float containing the longitude

Returns:
Result:
    'pass' [Parameter describing if the call went well or not]
    'message' [A message containing information about the result]
'''
def create_post(token, message, email, lat, long):
    if not (lat == 0 and long == 0):
        resp = requests.get("https://geocode.xyz/" +str(lat) +","+ str(long) +  "?json=1%22")
        data = resp.json()

        if ('success' in data and not data['success']):
            return {'pass': False, 'message': "We cannot post messages that fast, wait 2 secs and try again"}
        city = data['city']
        country = data['prov']
    else:
        city = "Unknown"
        country = "Unknown"

    result = database_helper.create_post(token, message, email, city, country)
    return result



'''
Generates a unique token

Returns:
String [A token]
'''
def generate_token():
    token = secrets.token_urlsafe(50)
    while (database_helper.Valid_Token_Check(token)):
        token = secrets.token_urlsafe(50)
    return token



'''
Logges in a user of the sufficient data is provided.

Parameters:
data: a json object containing the data

Returns:
Result:
    'pass' [Parameter describing if the call went well or not]
    'message' [A message containing information about the result]
'''
def sign_in(data):
    result = database_helper.find_user(data['email'], data['password'])
    if (result['pass']):
        database_helper.log_out_other_users(data['email'])
        token = generate_token()
        result = database_helper.log_in_user(data['email'], token)
    return result



'''
Changes the password of the user with the token if sufficient information is provided.

Parameters:
token: string
data: a json object containing the data

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'messages' [The messages]
'''
def change_password(token, data):
    res = database_helper.get_signed_in_user(token)
    if (res['pass']):
        res = database_helper.find_user(res['email'], data['oldpassword'])
        if(res['pass']):
            res = database_helper.update_password(res['email'], data['newpassword'])

    return res


'''
Send out an update to all sockets saying inf

Parameters:
inf: Dict containing information to be sent
Returns:
'''
def update_sockets(inf):
    for token in database_helper.signed_in_users:
        if database_helper.signed_in_users[token] is not None:
            database_helper.signed_in_users[token]['socket'].send(json.dumps(inf))



'''
Calulates and returns the number of people online with a spesific gender

Parameters:
gender: A string containing the gender
Returns:
int: the total number of people with that gender currently logged in
'''
def calculate_gender_stats(gender):
    total = 0
    for key, value in database_helper.signed_in_users.items():
        if str(value['information']['Gender']).lower() == gender:
            total += 1
    return total


'''
Remove a token and a socket together in the "signed_in_users" dict

Parameters:
token: string
socket
'''
def remove_socket(token):
    if (token in database_helper.signed_in_users):
        database_helper.signed_in_users[token]['socket'].close()
        del database_helper.signed_in_users[token]
        update_sockets({"type" : "stats", "numPeopleOnline" : {"total": len(database_helper.signed_in_users),
                                                                        "male": calculate_gender_stats("male"),
                                                                        "female": calculate_gender_stats("female"),
                                                                        "other": calculate_gender_stats("other")}})




'''
Adds a token and a socket together in the "signed_in_users" dict

Parameters:
token: string
socket: Socket object
'''
def add_socket_connection(token, socket):
    if database_helper.Valid_Token_Check(token):
        database_helper.signed_in_users[token] = {"socket": socket, "information": database_helper.get_user_data_by_token(token)['UserData']}
        update_sockets({"type" : "stats", "numPeopleOnline" : {"total": len(database_helper.signed_in_users),
                                                                        "male": calculate_gender_stats("male"),
                                                                        "female": calculate_gender_stats("female"),
                                                                        "other": calculate_gender_stats("other")}})
