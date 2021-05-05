import sqlite3
from flask import Flask, jsonify
from flask import g
import sys
import secrets
import json


import logic

DATABASE_URI = "database.db"

# Container containing signed in users and there information.
signed_in_users = {}




'''
Returns the database object if there is one, otherwise create one and then reutrn it.

Returns:
db [The databse object] 
'''
def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
    return db




'''
Safely disconnect the database
'''
def disconnect_db():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()
        g.db = None




'''
Takes in a token and checks if there is a user assigned to that token,
if thats the case then return that user's email.

Parameters:
token: string

Returns:
'pass' [Parameter describing if the call went well or not]
'pass' == False: 'message' [A message containing information about the result]
'pass' == True: 'email' [The email of the user]
'''
def get_signed_in_user(token):
    cursor = get_db().execute("SELECT * FROM SignedInUsers WHERE Token = ?;", [token])
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) != 1:
        if len(rows) == 0:
            return {'pass': False, 'message': "Not a valid token"}
        return {'pass': False, 'message': "Internal error"}
    return {'pass': True, 'email': rows[0][0]}




'''
Checks if the token is vaild, thereby if there is a user with that token in the database.

Parameters:
token: string

Returns:
Bool [Is the token valid?]
'''
def Valid_Token_Check(token):
    if (get_signed_in_user(token)['pass']):
        return True
    return False




'''
Creates a user in the database

Parameters:
email: string
fname: string
lname: string
password: string
gender: string
city: string
country: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'''
def create_user(email, fname, lname, password, gender, city, country):
    try:
        get_db().execute("INSERT INTO Users VALUES(?,?,?,?,?,?,?);",[email, fname, lname, password, gender, city, country])
        get_db().commit()

        return {'pass': True, 'message': "User was created"}
    except Exception as e:
        return {'pass': False, 'message': str(e)}




'''
Checks if there is a user with a certain email and password in the database,
if there exists sutch a user return that users email.

Parameters:
email: string
password: string

Returns:
'pass' [Parameter describing if the call went well or not]
'pass' == False: 'message' [A message containing information about the result]
'pass' == True: 'email' [The email of the user]
'''
def find_user(email, password):
    try:
        cursor = get_db().execute("SELECT * FROM Users WHERE Email = ? AND Psw = ?;", [email, password])
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) != 1:
            return {'pass': False, 'message': "Wrong email or password"}
        return {'pass': True, 'email': rows[0][0]}
    except Exception as e:
        return {'pass': False, 'message': str(e)}




'''
Adds a user to the databse containing all signed in users.

Parameters:
email: string
token: string

Returns:
'pass' [Parameter describing if the call went well or not]
'pass' == False: 'message' [A message containing information about the result]
'pass' == True: 'token' [The token of the user]
'''
def log_in_user(email, token):
    try:
        get_db().execute("INSERT INTO SignedInUsers VALUES(?,?);", [email, token])
        get_db().commit()
        return {'pass': True, 'token': token}
    except Exception as e:
        return {'pass': False, 'message': str(e)}




'''
Removes a user from the database containing all signed in users.

Parameters:
token: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'''
def remove_user(token):
    if Valid_Token_Check(token):
        try:
            get_db().execute("DELETE FROM SignedInUsers WHERE Token = ?;", [token])
            get_db().commit()
            logic.remove_socket(token)
            return {'pass': True, 'message': "User signed out"}
        except Exception as e:
            return {'pass': False, 'message': str(e)}
    else:
        return {'pass': False, 'message': "not a valid email or token"}




'''
Updates the password for a user with a certian email

Parameters:
email: string
newpass: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'''
def update_password(email, newpass):
    try:
        get_db().execute("UPDATE Users SET Psw = ? WHERE Email = ?;", [newpass, email])
        get_db().commit()

        return {'pass': True, 'message': "Password changed"}
    except Exception as e:
        return {'pass': False, 'message': str(e)}




'''
Checks if there exists a user with a certian email,
if there is sutch a user return that users information.

Parameters:
email: string

Returns:
'pass' [Parameter describing if the call went well or not]
'pass' == False: 'message' [A message containing information about the result]
'pass' == True: 'message' [A message containing inforamtion about the result]
                'UserData' [The data of the user]
'''
def get_user_data_by_email(email):
    try:
        cursor = get_db().execute("SELECT * FROM Users WHERE Email = ?;", [email])
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) != 1:
            return {'pass': False, 'message': "Internal error(4)"}

        result = {"Email": rows[0][0], "FirstName": rows[0][1], "FamilyName": rows[0][2],\
             "Gender": rows[0][4], "City": rows[0][5], "Country": rows[0][6]}
        return {'pass': True, 'message': "success", 'UserData': result}
    except Exception as e:
        return {'pass': False, 'message': str(e)}




'''
Checks if there exists a user with a certian token,
if there is sutch a user return that users information.

Parameters:
token: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'''
def get_user_data_by_token(token):
    try:
        emailReq = get_signed_in_user(token)
        if emailReq['pass']:
            return get_user_data_by_email(emailReq['email'])
        return {'pass': False, 'message': 'Could not find user!'}
    except Exception as e:
        return {'pass': False, 'message': str(e)}




'''
Adds a post in the database containing all messages.

Parameters:
token: string
message: string
email: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'''
def create_post(token, message, email, city, country):
    try:
        dataReq = get_user_data_by_token(token)
        if (dataReq['pass']):
            sender_email = dataReq['UserData']['Email']
            sender_gender = get_user_data_by_email(sender_email)['UserData']['Gender']
            get_db().execute("INSERT INTO Messages(ReceiverEmail, SenderEmail, Msg, City, Country, SenderGender) VALUES(?,?,?,?,?,?);", \
                [str(email), str(sender_email), str(message), str(city), str(country), str(sender_gender)])
            get_db().commit()
            return {'pass': True, 'message': "success, message posted if possible"}
        return {'pass': False, 'message': "Could not find that user"}
    except Exception as e:
        return {'pass': False, 'message': "Wait before posting another message"}




'''
Retrevies the messages sent by a user with a spesific token

Parameters:
token: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'''
def get_user_messages_by_token(token):
    try:
        sender_email = get_user_data_by_token(token)['UserData']['Email']
        return get_user_messages_by_email(token, sender_email)
    except Exception as e:
        return {'pass': False, 'message': str(e)}



'''
Retrevies the messages sent by a user with a spesific email

Parameters:
token: string
email: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'messages' [The messages]
'''
def get_user_messages_by_email(token, email):
    try:
        cursor = get_db().execute("SELECT * FROM Messages WHERE ReceiverEmail = ?;",[email])
        rows = cursor.fetchall()
        cursor.close()
        result = []
        for index in range(len(rows)):
            result.append({'Receiver':rows[index][1], 'Sender':rows[index][2], 'Message':rows[index][3], 'City':rows[index][4], 'Country':rows[index][5]})

        return {'pass': True, 'message': "success", 'messages': result}
    except Exception as e:
        return {'pass': False, 'message': str(e)}




'''
Logs out all users already logged in to a spesific email

Parameters:
email: string

Returns:
'pass' [Parameter describing if the call went well or not]
'message' [A message containing information about the result]
'''
def log_out_other_users(email):
    try:
        cursor = get_db().execute("SELECT * FROM SignedInUsers WHERE Email = ?;", [email])
        rows = cursor.fetchall()
        cursor.close()
        if (len(rows) > 0):
            for row in rows:
                token = row[1]
                remove_user(token)

        return {'pass': True, 'message': "User signed out"}
    except Exception as e:
        return {'pass': False, 'message': str(e)}



'''
Returns the total number of users ever created.

Parameters:

Returns:
int: Number of user created or the string "error" if something went wront.
'''
def users_total_stats():
    try:
        cursor = get_db().execute("SELECT * FROM Users;")
        rows = cursor.fetchall()
        cursor.close()
        total = len(rows)
        male = 0
        female = 0
        other = 0

        # This is poorly done (very slow) and we should probably save this information in the database
        # for use in the future. But we dont have time.
        for i in range(0, total):
            if (rows[i][4] == "Male"):
                male += 1
            elif (rows[i][4] == "Female"):
                female += 1
            else:
                other += 1

        return {"total": total, "male" : male, "female" : female, "other" : other}
    except:
        return "error"



'''
Returns the total number of posts ever created.

Parameters:

Returns:
int: Number of posts created or the string "error" if something went wront.
'''
def posts_stats():
    try:
        cursor = get_db().execute("SELECT * FROM Messages;")
        rows = cursor.fetchall()
        cursor.close()
        total = len(rows)


        cursor = get_db().execute("SELECT * FROM Messages WHERE SenderGender = ?;", ["Male"])
        rows = cursor.fetchall()
        cursor.close()
        male = len(rows)


        cursor = get_db().execute("SELECT * FROM Messages WHERE SenderGender = ?;", ["Female"])
        rows = cursor.fetchall()
        cursor.close()
        female = len(rows)


        cursor = get_db().execute("SELECT * FROM Messages WHERE SenderGender = ?;", ["Other"])
        rows = cursor.fetchall()
        cursor.close()
        other = len(rows)

        return({"total": total,
                    "male": male,
                    "female": female,
                    "other": other})

    except:
        return "error"