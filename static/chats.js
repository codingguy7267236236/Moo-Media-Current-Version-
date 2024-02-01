function loadChats(data){
  var hld = document.getElementById("chats");
  for(let i=0; i<data.length; i++){
    var chat = createChat(data[i]);
    hld.appendChild(chat);
  }
}

function createChat(data){
  var chat = document.createElement("div");
  chat.setAttribute("class","chat");
  chat.setAttribute("onclick",`location.href='/message/${data[0]}'`);

  var img = document.createElement("img");
  img.setAttribute("src",`/static/${data[2]}`);
  chat.appendChild(img);

  var un = document.createElement("h3");
  un.innerHTML = data[1];
  chat.appendChild(un);
  return chat
}

function loadChatId(chatId,un,pfp){
  localStorage.setItem("chatId",chatId);
  localStorage.setItem("un",un);
  localStorage.setItem("pfp",pfp);
}

function loadMessages(data,un){
  var hld = document.getElementById("msgs");
  for(let i=0; i<data.length; i++){
    var msg = createMsg(data[i],un);
    hld.appendChild(msg);
  }
}

function createMsg(data,username){
  var msg = document.createElement("div");
  msg.setAttribute("class","msg");

  var im = document.createElement("img");
  im.setAttribute("src",`/static/${data[3]}`);
  msg.appendChild(im);

  var div = document.createElement("div");
  msg.appendChild(div);

  var un = document.createElement("h3");
  un.innerHTML=data[2];
  div.appendChild(un);

  var txt = document.createElement("p");
  txt.innerHTML = data[1];
  div.appendChild(txt);

  //checking if message sender is user
  if(username==data[2]){
    div.setAttribute("class","msgYou");
    un.innerHTML="You"
  }else{
    div.setAttribute("class","msgOth");
  }
  return msg;
}

async function sendMsg(){
  var msg = document.getElementById("msg");
  await fetch(`[url of flask app]/sendMsg`,{
    method:"POST",
    body:JSON.stringify({
      msg:msg.value,
      chatId:localStorage.getItem("chatId")
    }),
    headers: {
      "Content-type": "application/json"
    }
  });
  //creating new message to show on screen
  var ms = createMsg(["",msg.value,localStorage.getItem("un"),localStorage.getItem("pfp")],localStorage.getItem("un"));
  var hld=document.getElementById("msgs");
  hld.insertBefore(ms,hld.firstChild);

  //resetting the message inout box
  var inp = document.getElementById("msg");
  inp.innerHTML = "";
  inp.value="";
}