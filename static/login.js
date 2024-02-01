localStorage.setItem("token","");
var log = document.getElementById("login");
var sign = document.getElementById("signup");

function login(){
    var log = document.getElementById("login");
    var sign = document.getElementById("signup");
    log.setAttribute("class","");
    sign.setAttribute("class","disable");
}

function signup(){
    var log = document.getElementById("login");
    var sign = document.getElementById("signup");
    log.setAttribute("class","disable");
    sign.setAttribute("class","");
}