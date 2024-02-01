from flask import Flask, session, render_template, url_for,request,redirect,jsonify, make_response,after_this_request
import jwt
import os
from functools import wraps
from funcs import createToken, Database, followGen, likeGen, updateUserToken,totalFollowers,clearToken


app = Flask(__name__)
app.config["SECRET_KEY"] = "ejrkjwj33483443ujfddfmf"
UPLOAD_FOLDER = "./static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


expir = 60*60*24

db = Database("db.db")
print(db.Command("SELECT * FROM users"))
#db.Command("CREATE TABLE IF NOT EXISTS messages(Id INTEGER PRIMARY KEY AUTOINCREMENT, chat INTEGER, user INTEGER, msg INTEGER)")

def token_required(f):
  @wraps(f)
  def decorated(*args,**kwargs):
    try:
      token = request.cookies.get("token")
      if not token:
        return redirect(url_for('login'))

      try:
        data = jwt.decode(jwt=token,key=app.config["SECRET_KEY"],algorithms=["HS256"])
      except:
        return redirect(url_for('login'))
      return f(*args,**kwargs)
    except KeyError:
      return redirect(url_for('login'))
  return decorated


def decodeToken(token):
  try:
    data = jwt.decode(jwt=token,key=app.config["SECRET_KEY"],algorithms=["HS256"])
  except:
    data = None
  return data

@app.route('/')
def index():
  return redirect(url_for("home"))

@app.route('/login')
def login():
  return render_template("login.html")

@app.route('/home')
@token_required
def home():
  cookie = request.cookies.get("token")
  data = decodeToken(cookie)

  toke = request.cookies.get("token")
  token = decodeToken(toke)

  #fetching posts not related to user
  posts = db.Command("SELECT posts.Id,posts.content,posts.imgs,users.username,users.pfp,posts.likes,posts.user FROM posts INNER JOIN users on users.Id = posts.user WHERE posts.user != ? AND posts.type=0 ORDER BY posts.Id DESC",(token["user"][0],))
  return render_template("home.html",dat=data,posts=posts,toke=toke,token=token)

@app.route('/shop')
@token_required
def shop():
  cookie = request.cookies.get("token")
  data = decodeToken(cookie)

  toke = request.cookies.get("token")
  token = decodeToken(toke)

  #fetching store items
  items = db.Command("SELECT items.Id,items.name,items.price, items.description,items.img,items.imgs,users.username FROM items INNER JOIN users on users.Id = items.user ORDER BY items.Id DESC")
  return render_template("store.html",dat=data,shop=items,toke=toke,token=token)


@app.route('/profile/<username>')
def profile(username):
  try:
    #get usrdetails
    usrDets = db.Command("SELECT Id,username,pfp,followers,bio,banner FROM users WHERE username=?",(username,))
    usrDets = usrDets[0]
    #print("prof dat",usrDets)
    id = usrDets[0]
    flws = totalFollowers(id,db)
    usrDets = list(usrDets)
    usrDets[3] = flws

    #getting user data from token if signed in
    try:
      token = request.cookies.get("token")
      token = decodeToken(token)
    except:
      token = None
    #fetching posts not related to user
    posts = db.Command("SELECT posts.Id,posts.content,posts.imgs,users.username,users.pfp,posts.likes,posts.user FROM posts INNER JOIN users on users.Id = posts.user WHERE posts.user = ? AND posts.type=0 ORDER BY posts.Id DESC",(id,))

    #fetching items
    items = db.Command("SELECT items.Id,items.name,items.price, items.description,items.img,items.imgs,users.username FROM items INNER JOIN users on users.Id = items.user WHERE items.user = ? ORDER BY items.Id DESC",(id,))

    #getting post number
    try:
      postNum = db.Command("SELECT COUNT(Id) FROM posts WHERE user=? AND type=0",(id,))
      postNum = postNum[0][0]
    except IndexError:
      postNum=0

    #checking if user follows this user or not
    try:
      res = db.Command("SELECT Id FROM following WHERE user=? AND follower=?",(id,token["user"][0]))
      res=res[0][0]
      flw = 1
    except IndexError:
      flw = 0

    #getting current users balance
    try:
      balance = db.Command("SELECT money FROM users WHERE Id=?",(token["user"][0],))
      balance = balance[0][0]
    except:
      balance = 0

    #getting followers and following
    followers=db.Command("SELECT users.username,users.pfp FROM users INNER JOIN following ON following.follower=users.Id WHERE following.user=?",(id,))
    following=db.Command("SELECT users.username,users.pfp FROM users INNER JOIN following ON following.user=users.Id WHERE following.follower=?",(id,))
    usrDets.append(len(following))
    followData = [followers,following]

    return render_template("profile.html",usr=usrDets,dat=token,posts=posts,postNum=postNum,shop=items,flw=flw,money=balance,token=token,flwData=followData)
  except Exception as e:
    print(e)
    return redirect(url_for("index"))


@app.route('/usrprofile',methods=["POST","GET"])
@token_required
def usrprofile():
  token = request.cookies.get("token")
  token = decodeToken(token)
  return redirect(url_for("profile",username=token["user"][1]))

@app.route('/viewpost/<id>')
@token_required
def viewpost(id):
  token = request.cookies.get("token")
  token = decodeToken(token)

  #getting the main post data
  main = db.Command("SELECT posts.Id,posts.content,posts.imgs,users.username,users.pfp,posts.likes,posts.user FROM posts INNER JOIN users on users.Id=posts.user WHERE posts.Id=?",(id,))

  #getting replies
  reps = db.Command("SELECT posts.Id,posts.content,posts.imgs,users.username,users.pfp,posts.likes,posts.user FROM posts INNER JOIN users on users.Id = posts.user WHERE posts.post = ? AND posts.type=1 ORDER BY posts.Id DESC",(id,))
  return render_template("viewpost.html",usr=token["user"],post=main,postId=id,replies=reps,token=token)


@app.route('/messages')
@token_required
def messages():
  token = request.cookies.get("token")
  token = decodeToken(token)
  #fetch users chats
  uid=token["user"][0]
  chats = db.Command("SELECT chats.Id,users.username,users.pfp FROM chats INNER JOIN users ON IIF(user1=?,chats.user2=users.Id,chats.user1=users.Id) WHERE user1=? OR user2=?",(uid,uid,uid))
  #print("Chat details",chats)
  return render_template("messages.html",usr=token["user"],token=token,chats=chats)

@app.route('/message/<id>')
@token_required
def message(id):
  token = request.cookies.get("token")
  token = decodeToken(token)
  uid=token["user"][0]
  #seeing if chat between two users exists
  try:
    res=db.Command("SELECT chats.Id,users.username,users.pfp FROM chats INNER JOIN users ON IIF(user1=?,chats.user2=users.Id,chats.user1=users.Id) WHERE (user1=? OR user2=?) AND chats.Id=?",(uid,uid,uid,id))
    res = res[0]
    #getting chat messages
    msgs = db.Command("SELECT messages.Id,messages.msg,users.username,users.pfp FROM messages INNER JOIN users ON messages.user=users.Id WHERE messages.chat=? ORDER BY messages.Id DESC",(id,))
  except IndexError:
    mId=db.Command("INSERT INTO chats (user1,user2) VALUES(?,?) RETURNING Id",(uid,id))
    mId=mId[0][0]
    return redirect(url_for("message",id=mId))
  return render_template("chat.html",usr=token["user"],msgs=msgs,chat=res,token=token)


@app.route('/edit')
@token_required
def edit():
  token = request.cookies.get("token")
  token = decodeToken(token)
  return render_template("edit.html",usr=token["user"],token=token)

@app.route('/addItem')
@token_required
def addItem():
  token = request.cookies.get("token")
  token = decodeToken(token)
  return render_template("addToStore.html",usr=token["user"],token=token)

@app.route('/sendMsg',methods=["POST"])
@token_required
def sendMsg():
  token = request.cookies.get("token")
  token = decodeToken(token)
  #getting posted data
  content_type = request.headers.get('Content-Type')
  if (content_type == 'application/json'):
    json = request.json
    print("Data:",json)
    #checking user is part of chat
    try:
      res = db.Command("SELECT Id FROM chats WHERE user1=? OR user2=?",(token["user"][0],token["user"][0]))
      id=res[0][0]
      #adding message
      db.Command("INSERT INTO messages (chat,user,msg) VALUES(?,?,?)",(id,token["user"][0],json["msg"]))
      return jsonify("Sent")
    except Exception as e:
      print(e)
      return jsonify("Access Denied")

  return jsonify("Error Sending")

@app.route('/addItemToDB',methods=["POST"])
@token_required
def addItemToDB():
  token = request.cookies.get("token")
  token = decodeToken(token)

  #getting posted data
  if request.method=="POST":
    desc=request.form.get("desc")
    name=request.form.get("name")
    price=request.form.get("price")

    try:
      hourly = request.form.get("hourly")
      if hourly=="on" or hourly=="true":
        hourly = True
      else:
        hourly = False
    except Exception as e:
      hourly = False

    res = db.Command("INSERT INTO items(name,price,description,user,hourly) VALUES(?,?,?,?,?) RETURNING Id",(name,price,desc,token["user"][0],hourly))
    pid = res[0][0]
    print("Product Id",pid)
    #cover image stuff
    files = request.files
    file = files["img"]

    #saving file
    imPath = f"{app.config['UPLOAD_FOLDER']}/coverImg_{pid}.png"
    dbPath = f"uploads/coverImg_{pid}.png"
    try:
      file.save(imPath)
      db.Command("UPDATE items SET img=? WHERE Id=?",(dbPath,pid))
    except:
      print("error")
  return render_template("addToStore.html",usr=token["user"])


@app.route('/post',methods=["POST","GET"])
@token_required
def post():
  if request.method=="POST":
    cont=request.form.get("content")

    #user info
    token = request.cookies.get("token")
    token = decodeToken(token)

    #getting follower info for like generation
    flws = db.Command(f"SELECT followers FROM users WHERE Id=?",params=(token["user"][0],))
    try:
      flws = flws[0][0]
    except IndexError:
      flws = 0
    #generating likes
    likes = likeGen(flws)
    res=db.Command("INSERT INTO posts (user,content,likes,type) VALUES(?,?,?,?) RETURNING Id;",(token["user"][0],cont,likes,0))
    id=res[0][0]

    #updating the followers
    flws = followGen(flws)
    db.Command("UPDATE users SET followers=? WHERE Id=?",(flws,token["user"][0]))

    #sorting out any uploaded files
    files = request.files.getlist("uploads")
    n=1
    for i in files:
      if i.filename=="" or i.filename==None:
        pass
      else:
        #saving file
        imPath = f"{app.config['UPLOAD_FOLDER']}/posts/{id}post_{n}.png"
        dbPath = f"uploads/posts/{id}post_{n}.png"
        #print(imPath)
        try:
          i.save(imPath)
          #update database
          db.Command("INSERT INTO imgs (post,img) VALUES(?,?)",(id,dbPath))
          n+=1
        except Exception as e:
          print(e)
          pass


    #updating usertokendata stuff
    dat = updateUserToken(db,token["user"][0])
    print(dat)
    @after_this_request
    def after_index(response):
      token = createToken(dat,app)
      response.set_cookie("token",token,max_age=expir)
      return response

  token = request.cookies.get("token")
  token = decodeToken(token)

  return render_template("post.html",token=token)


@app.route('/reply/<id>',methods=["POST","GET"])
@token_required
def reply(id):
  if request.method=="POST":
    cont=request.form.get("content")

    #user info
    token = request.cookies.get("token")
    token = decodeToken(token)

    #getting follower info for like generation
    flws = db.Command(f"SELECT followers FROM users WHERE Id=?",params=(token["user"][0],))
    try:
      flws = flws[0][0]
    except IndexError:
      flws = 0
    #generating likes
    likes = likeGen(flws)
    db.Command("INSERT INTO posts (user,content,likes,type,post) VALUES(?,?,?,?,?)",(token["user"][0],cont,likes,1,id))

    #updating the followers
    flws = followGen(flws)
    db.Command("UPDATE users SET followers=? WHERE Id=?",(flws,token["user"][0]))

    #updating usertokendata stuff
    dat = updateUserToken(db,token["user"][0])
    print(dat)
    @after_this_request
    def after_index(response):
      token = createToken(dat,app)
      response.set_cookie("token",token,max_age=expir)
      return response

  return redirect(f"/viewpost/{id}")

@app.route('/auth1',methods=["POST","GET"])
def auth1():
  if request.method=="POST":
    un=request.form.get("username")
    pw=request.form.get("password")
    try:
      res = db.Command(f"SELECT Id,username,pfp,bio FROM users WHERE username=? AND password=?",(un,pw))
      dat = res[0]
      @after_this_request
      def after_index(response):
        token = createToken(dat,app)
        response.set_cookie("token",token,max_age=expir)
        return response

      #print("Cookie value",request.cookies.get("token"))
      return redirect(url_for("home"))
    except IndexError:
      return redirect(url_for("login"))
  return redirect(url_for("login"))

@app.route('/auth2',methods=["POST","GET"])
def auth2():
  if request.method=="POST":
    un=request.form.get("username")
    pw=request.form.get("password")
    try:
      res = db.Command(f"SELECT Id,username,pfp FROM users WHERE username=?",(un,))
      dat = res[0]
      return redirect(url_for("login"))
    except IndexError:
      flws = 0
      res=db.Command(f"INSERT INTO users(username,password,followers,bio,money) VALUES(?,?,?,'',1000) RETURNING Id,username,pfp;",(un,pw,flws))
      dat = res[0]
      @after_this_request
      def after_index(response):
        token = createToken(dat,app)
        response.set_cookie("token",token,max_age=expir)
        return response
      return redirect(url_for("home"))
  return redirect(url_for("login"))



@app.route('/profileUpdate',methods=["POST"])
@token_required
def profileUpdate():
  if request.method=="POST":
    un=request.form.get("usrname")
    bio=request.form.get("bio")

    #fetching token data
    token = request.cookies.get("token")
    token = decodeToken(token)

    uId = token["user"][0]

    #processing update stuff

    #seeing whether to update username or not
    try:
      #IF USERNAME ALREADY EXISTS DO NOTHING
      res = db.Command(f"SELECT Id,username,pfp,bio FROM users WHERE username=?",(un,))
      yep = res[0]
    except IndexError:
      db.Command("UPDATE users SET username=?, WHERE Id=?",(un,uId))

    db.Command("UPDATE users SET bio=? WHERE Id=?",(bio,uId))


    #pfp stuff
    files = request.files
    file = files["pfp"]
    banner = files["banner"]

    if file.filename == "":
      print("No pfp selected")
    else:
      #saving file
      imPath = f"{app.config['UPLOAD_FOLDER']}/pfp/{uId}pfp.png"
      dbPath = f"uploads/pfp/{uId}pfp.png"
      #print(imPath)
      try:
        file.save(imPath)
        #update database
        db.Command("UPDATE users SET pfp=? WHERE Id=?",(dbPath,uId))
      except:
        print("Couldn't upload file")

    if banner.filename == "":
      print("No banner selected")
    else:
      #saving banner file
      imPath = f"{app.config['UPLOAD_FOLDER']}/banners/{uId}banner.png"
      dbPath = f"uploads/banners/{uId}banner.png"
      #print(imPath)
      try:
        banner.save(imPath)
        #update database
        db.Command("UPDATE users SET banner=? WHERE Id=?",(dbPath,uId))
      except:
        print("Couldn't upload file")



    #updating users cookie data token
    #res = db.Command(f"SELECT Id,username,pfp FROM users WHERE Id=?",(uId,))
    dat = updateUserToken(db,uId)
    @after_this_request
    def after_index(response):
      token = createToken(dat,app)
      response.set_cookie("token",token,max_age=expir)
      return response

    #fetching new token data
    token = request.cookies.get("token")
    token = decodeToken(token)
    #db.Command("INSERT INTO posts (user,content) VALUES(?,?)",(token["user"][0],cont))
  return redirect(url_for("profile",username=token["user"][1]))


@app.route('/product/<id>')
@token_required
def product(id):
  token = request.cookies.get("token")
  token = decodeToken(token)
  res = db.Command("SELECT items.Id, items.user,items.name,items.img,items.imgs,items.price,items.description,items.hourly,items.category,items.rating,users.username,users.pfp FROM items INNER JOIN users ON items.user=users.id WHERE items.Id=?",(id,))
  return render_template("product.html",item=res[0],user=token["user"],token=token)

@app.route('/logout')
@token_required
def logout():
  @after_this_request
  def after_index(response):
    response.delete_cookie("token")
    return response
  return redirect(url_for("login"))


@app.route('/delPost/<id>')
@token_required
def delPost(id):
  token = request.cookies.get("token")
  token = decodeToken(token)
  usr = token["user"]
  print("current id here",usr[0])
  #checking user is the owner of the post
  try:
    res=db.Command("SELECT Id FROM posts WHERE Id=? AND user=?",(id,usr[0]))
    res = res[0][0]
    db.Command("DELETE FROM posts WHERE Id=? OR (post=? AND (type=1 OR type=2))",(id,id))
    imgs = db.Command("SELECT img FROM imgs WHERE post=?",(id,))
    for im in imgs:
      os.remove(f"./static/{im[0]}")
    db.Command("DELETE FROM imgs WHERE post=?",(id,))
    return jsonify("Post deleted successfully")
  except Exception as e:
    return jsonify(f"Error deleting this post, {e}")


@app.route('/likepost/<id>',methods=["GET"])
def likepost(id):
  token = request.args.get('token')
  token = decodeToken(token)
  usr = token["user"]
  #checking user is the owner of the post
  try:
    res=db.Command("SELECT Id FROM posts WHERE post=? AND type=2 AND user=?",(id,usr[0]))
    res = res[0][0]
    print("id",res)
    db.Command("DELETE FROM posts WHERE Id=?",(res,))
    return jsonify("unlike")
  except IndexError:
    db.Command(f"INSERT INTO posts (user,post,type) VALUES(?,?,2)",(usr[0],id))
    return jsonify("like")


@app.route('/getPostData/<id>',methods=["GET"])
def getPostData(id):
  #getting replies
  res = db.Command("SELECT COUNT(Id) FROM posts WHERE type=1 AND post=?",(id,))
  try:
    replys = res[0][0]
  except IndexError:
    replys = 0

  #getting likes
  res = db.Command("SELECT COUNT(Id) FROM posts WHERE type=2 AND post=?",(id,))
  try:
    usrLikes = res[0][0]
    res = db.Command("SELECT likes FROM posts WHERE Id=?",(id,))
    likes = usrLikes+res[0][0]
  except IndexError:
    likes = 0

  #getting any images part of the post
  res = db.Command("SELECT img FROM imgs WHERE post=?",(id,))
  data = [replys,likes,res]
  return jsonify(data)

@app.route('/debug/<name>',methods=["GET"])
def debug(name):
  res = db.Command(f"SELECT * FROM {name}")
  try:
    res = res
  except IndexError:
    res = 0
  return jsonify(res)

@app.route('/getLikeNum/<id>',methods=["GET"])
def getLikeNum(id):
  res = db.Command("SELECT COUNT(Id) FROM posts WHERE type=2 AND post=?",(id,))
  try:
    usrLikes = res[0][0]
    res = db.Command("SELECT likes FROM posts WHERE Id=?",(id,))
    likes = usrLikes+res[0][0]
  except IndexError:
    likes = 0
  return jsonify(likes)


@app.route('/getFollowNum/<id>',methods=["GET"])
def getLFollowNum(id):
  likes = totalFollowers(id,db)
  return jsonify(likes)


@app.route('/follow/<id>',methods=["GET"])
def follow(id):
  token = request.cookies.get("token")
  token = decodeToken(token)

  #seeing if user already follows
  try:
    res=db.Command("SELECT Id FROM following WHERE user=? AND follower=?",(id,token["user"][0]))
    res=res[0][0]
    db.Command("DELETE FROM following WHERE user=? AND follower=?",(id,token["user"][0]))
    return jsonify("unfollowed")
  except IndexError:
    db.Command("INSERT INTO following (user,follower) VALUES(?,?)",(id,token["user"][0]))
    return jsonify("followed")


@app.route('/deleteproduct/<id>')
@token_required
def deleteproduct(id):
  token = request.cookies.get("token")
  token = decodeToken(token)
  #checking user is the seller otherwise do nothing
  try:
    res = db.Command("SELECT img FROM items WHERE user=? AND Id=?",(token["user"][0],id))
    res = res[0][0]
    #delete the file if exists
    try:
      os.remove(f"./static/{res}")
    except Exception as e:
      print(e)
    #user does own this so can delete
    db.Command("DELETE FROM items WHERE Id=?",(id,))
  except IndexError:
    pass
  return redirect(url_for("usrprofile"))


@app.route('/buy/<id>',methods=["POST"])
@token_required
def buy(id):
  token = request.cookies.get("token")
  token = decodeToken(token)

  if request.method=="POST":
    price = db.Command("SELECT price FROM items WHERE Id=?",(id,))
    price = price[0][0]
    try:
      hrs=request.form.get("hours")
    except:
      hrs = 1
    price = float(price)*float(hrs)
    #checking if user has enough money
    money = db.Command("SELECT money FROM users WHERE Id=?",(token["user"][0],))
    money = money[0][0]

    if float(money) >= float(price):
      print("Transaction successful")
      #remove and add funds respectively
      money = float(money)-float(price)
      db.Command("UPDATE users SET money=? WHERE Id=?",(money,token["user"][0]))
      #sellers update 
      sell1 = db.Command("SELECT users.Id,users.money FROM users INNER JOIN items ON users.Id = items.user WHERE items.Id=?",(id,))
      sell = sell1[0][1]
      sellId = sell1[0][0]
      sell = float(sell)+float(price)
      db.Command("UPDATE users SET money=? WHERE Id=?",(sell,sellId))
    else:
      print("Insufficient Funds")

  return redirect(url_for("shop"))

app.run(host='0.0.0.0', port=8080)
