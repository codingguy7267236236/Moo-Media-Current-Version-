import json
import jwt
import datetime
import sqlite3
import random

expire = 60*24

def createToken(user,app):
  try:
    token = jwt.encode({"user":user, "exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=expire)}, app.config["SECRET_KEY"])
  except:
    token = None
  return token

def clearToken(app):
  try:
    token = jwt.encode({"user":"", "exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=expire)}, app.config["SECRET_KEY"])
  except:
    token = None
  return token


class Database():
  def __init__(self,path):
    self.path = path

  def Connect(self):
    self.connection = sqlite3.connect(self.path)
    self.cursor = self.connection.cursor()

  def Close(self):
    self.connection.close()

  def Command(self,sql,params=None):
    self.Connect()
    #if no params defined
    if params == None:
      self.cursor.execute(sql)

    #params parameter used incase the sql statement includes binding placeholders
    else:
      self.cursor.execute(sql,params)
    result = self.cursor.fetchall()
    #saves the changes to the database
    self.connection.commit()
    self.Close()
    return result


def likeGen(flws):
  likes = 0
  flws = int(flws)
  max = flws*0.2
  if max <= 0:
    max = 1

  likes = random.randint(0,int(max))
  print(f"Likes: ",likes)
  return likes


def followGen(flws):
  flws = int(flws)
  if flws < 1000:
    max = 10 + (flws*0.1)
  else:
    max = flws*0.1

  if max <= 0:
    max = 1

  flws += random.randint(int((max*-1)/2),int(max))
  if flws < 0:
    flws = 0
  print(f"Followers: ",flws)
  return flws


def updateUserToken(db,uId):
  res = db.Command(f"SELECT Id,username,pfp,followers,bio FROM users WHERE Id=?",(uId,))
  dat = res[0]
  return dat


def totalFollowers(id,db):
  res = db.Command("SELECT COUNT(Id) FROM following WHERE user=?",(id,))
  try:
    usrLikes = res[0][0]
    res = db.Command("SELECT followers FROM users WHERE Id=?",(id,))
    likes = usrLikes+res[0][0]
  except IndexError:
    likes = 0
  return likes


  #####TABLES
  #users(Id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, pfp TEXT, bio TEXT, followers INTEGER, money FLOAT, banner TEXT)
  #posts(Id INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER, content TEXT, imgs INTEGER, likes INTEGER, type INTEGER, post INTEGER)
#items(Id INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER, name TEXT, img TEXT, imgs INTEGER, price FLOAT, description TEXT, hourly BOOL, category INTEGER, rating INTEGER)
#following(Id INTEGER PRIMARY KEY AUTOINCREMENT, user INTEGER, follower INTEGER)
#imgs(Id INTEGER PRIMARY KEY AUTOINCREMENT, post INTEGER, img TEXT)
#chats(Id INTEGER PRIMARY KEY AUTOINCREMENT, user1 INTEGER, user2 INTEGER)
#messages(Id INTEGER PRIMARY KEY AUTOINCREMENT, chat INTEGER, user INTEGER, msg INTEGER)
