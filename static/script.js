//api url
const api = "[url of flask app here we a / at the end]";


async function createPosts(data,uid){
    var holder = document.getElementById("feedHldrs");
    holder.innerHTML = "";
    //looping other all posts data
    for(let i=0; i<data.length; i++){
        var pst = await createPost(data[i],uid);
        holder.appendChild(pst);
        //holder.insertBefore(pst,holder.firstChild);
    }
}


async function createPost(data,uid){
    var post = document.createElement("div");
    post.setAttribute("class","post");
    post.setAttribute("id",`post_${data[0]}`)

    //id input value
    var idInp = document.createElement("input");
    idInp.setAttribute("type","hidden");
    idInp.value = data[0];
    idInp.setAttribute("id",`id_${data[0]}`);
    post.appendChild(idInp);

    var img = document.createElement("img");
    //checking if user has pfp or not
    //setting source as default pfp to begin with and should change if the user has set one
    var src = "https://i.pinimg.com/550x/8f/e6/66/8fe66626ec212bb54e13fa94e84c105c.jpg";
    //seeing if user has a pfp set
    if(data[4] != null && data[4] != ""){
        src = `/static/${data[4]}`;
    }
    img.setAttribute("src",src);
    img.setAttribute("onclick",`location.href='/profile/${data[3]}'`);
    post.appendChild(img);

    var txtSec = document.createElement("div");
    post.appendChild(txtSec);

    var usrnam = document.createElement("h3");
    txtSec.appendChild(usrnam);
    usrnam.innerHTML = data[3];
    usrnam.setAttribute("onclick",`location.href='/profile/${data[3]}'`);

    var cont = document.createElement("p");
    txtSec.appendChild(cont);
    cont.innerHTML = data[1];
    cont.setAttribute("onclick",`location.href='/viewpost/${data[0]}'`);
    //getting image holder thing
    var imgHld = document.createElement("div");
    imgHld.setAttribute("class","imageHolder");
    imgHld.setAttribute("onclick",`location.href='/viewpost/${data[0]}'`);
    txtSec.append(imgHld);

    //getting post data such as likes,replys and imgs
    var dat = await fetch(`${api}/getPostData/${data[0]}`);
    dat = await dat.json();
    //creating all the images for this post
    for(let i=0; i<dat[2].length;i++){
      //console.log("File",dat[2][i][0]);
      var im = document.createElement("img");
      im.setAttribute("src",`/static/${dat[2][i][0]}`);
      imgHld.appendChild(im);
    }


    //footer stuff
    var foot = document.createElement("div");
    foot.setAttribute("class","postfoot");
    txtSec.appendChild(foot);
    //likes stuff
    var likes = document.createElement("div");
    likes.setAttribute("class","likes");
    var heart = document.createElement("img");
    heart.setAttribute("src","https://icons.veryicon.com/png/o/miscellaneous/ui-basic-linear-icon/like-106.png");
    heart.setAttribute("onclick",`likepost(${data[0]})`);
    likes.appendChild(heart);
    foot.appendChild(likes);
    var lik = document.createElement("p");
    lik.setAttribute("id",`likeNum_${data[0]}`);
  //calling api to calculate number of likes
    lik.innerHTML=dat[1];
    likes.appendChild(lik);

    //reply stuff
    likes = document.createElement("div");
    likes.setAttribute("class","likes");
    heart = document.createElement("img");
    heart.setAttribute("src","https://cdn-icons-png.flaticon.com/512/3388/3388675.png");
    heart.setAttribute("onclick",`location.href='/viewpost/${data[0]}'`);
    likes.appendChild(heart);
    foot.appendChild(likes);

    var replies = document.createElement("p");
    replies.setAttribute("id",`replyNum_${data[0]}`);
  likes.appendChild(replies);
    replies.innerHTML = dat[0];

    //if current user posted this post delete button added
    if(uid == data[6]){
        var bin = document.createElement("div");
        bin.setAttribute("class","likes");
        var icon = document.createElement("img");
        icon.setAttribute("src","https://cdn-icons-png.flaticon.com/512/3405/3405244.png");
        icon.setAttribute("onclick",`deletePost(${data[0]})`);
        bin.appendChild(icon);
        foot.appendChild(bin);
    }

    return post;
}


async function loadViewPost(main,replies,uid){
    var holder = document.getElementById("replies");
    holder.innerHTML = "";

    var mainHld = document.getElementById("mainPost");
    for(let i=0; i<main.length; i++){
        var mainPost = await createPost(main[i],uid);
        //holder.appendChild(pst);
        mainHld.appendChild(mainPost);
    }
    //looping other all posts data
    for(let i=0; i<replies.length; i++){
        var pst = await createPost(replies[i],uid);
        holder.appendChild(pst);
        //holder.insertBefore(pst,holder.firstChild);
    }
}


async function deletePost(id){
    var dat = await fetch(`${api}/delPost/${id}`);
    dat = dat.json();
    var pst = document.getElementById(`post_${id}`);
    pst.remove();
}

function usrSec(id){
    var ids = ["storeUsr","postsUsr"];
    var hlds = ["feedHldrs","storeHldr"];

    var cls = ["feed","storeUsr"]

    for(let i=0; i<ids.length; i++){
        var sec = document.getElementById(ids[i]);
        var hld = document.getElementById(hlds[i])
        if(i==id){
            sec.setAttribute("class","selected");
            hld.setAttribute("class",cls[i]);
        }
        else{
            sec.setAttribute("class","");
            hld.setAttribute("class","disable");
        }
    }
}

async function likepost(id){
  var dat = await fetch(`${api}/likepost/${id}?token=${localStorage.getItem("token")}`);
  dat = await dat.json();
  //updating like background pink if user likes non if not
  //updating div element with number of likes
  var likes = document.getElementById(`likeNum_${id}`);
  var llikes = await fetch(`${api}/getLikeNum/${id}`);
  llikes = await llikes.json();
  likes.innerHTML = llikes;
}


async function follow(id){
  var dat = await fetch(`${api}/follow/${id}?token=${localStorage.getItem("token")}`);
  dat = await dat.json();
  var flwBtn = document.getElementById("flwBtn")
  //setting follow button
  if(dat=="followed"){
    flwBtn.innerHTML = "FOLLOWING";
    flwBtn.setAttribute("class","button green");
  }
  else{
    flwBtn.innerHTML = "FOLLOW";
    flwBtn.setAttribute("class","button");
  }

  //updating users following count on screen
  var flws = await fetch(`${api}/getFollowNum/${id}`);
  flws = await flws.json();
  var followers = document.getElementById("followers");
  followers.innerHTML = `Followers: ${flws}`;
}

function loadShopItems(data){
  var holder =  document.getElementById("storeHldr");
  holder.innerHTML = "";
  for(let i=0; i<data.length; i++){
    var item = createItem(data[i]);
    holder.appendChild(item);
  }
}

function createItem(data){
  var item = document.createElement("div");
  item.setAttribute("class","shopItem");
  item.setAttribute("onclick",`location.href='/product/${data[0]}'`)
  item.style.backgroundImage=`linear-gradient(rgba(0,0,0,0.4),rgba(0,0,0,0.4)),url('/static/${data[4]}')`

  //details sec
  var dets = document.createElement("div");
  dets.setAttribute("class","details");
  item.appendChild(dets);

  //div bit
  var div = document.createElement("div");
  dets.appendChild(div);

  var product = document.createElement("h3");
  product.innerHTML = data[1];
  div.appendChild(product);

  var price = document.createElement("h4");
  price.innerHTML = `$${data[2]}`;
  div.appendChild(price);

  return item;
}


function storeToken(data){
  localStorage.setItem("token",data);
}

//follwo section
function createFollow(data){
  //console.log("data",data);
  var div = document.createElement("div");
  div.setAttribute("onclick",`location.href='/profile/${data[0]}'`);

  var im = document.createElement("img");
  im.setAttribute("src",`/static/${data[1]}`);
  div.appendChild(im);
  var un = document.createElement("h3");
  un.innerHTML=data[0];
  div.appendChild(un);
  return div;
}

function loadFollow(data){
  for(let i=0; i<data.length; i++){
    if(i==0){
      loadFollowers(data[0]);
    }else{
      loadFollowing(data[1]);
    }
  }
}

function loadFollowers(data){
  var hld = document.getElementById("followerss2");
  for(let i=0; i<data.length; i++){
    var flw = createFollow(data[i])
    hld.appendChild(flw);
  }
}

function loadFollowing(data){
  var hld = document.getElementById("followings2");
  for(let i=0; i<data.length; i++){
    var flw = createFollow(data[i])
    hld.appendChild(flw);
  }
}

function flwpost(type){
  var hlds = ["followerss","followings","feedHldrs"];
  var act = ["","","feed"];
  for(let i=0; i<hlds.length; i++){
    var hld = document.getElementById(hlds[i]);
    if(hlds[i]==type){
      hld.setAttribute("class",act[i]);
    }
    else{
      hld.setAttribute("class","disable");
    }
  }
}