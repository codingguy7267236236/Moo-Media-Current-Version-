function displayProduct(data){
  var banner = document.getElementById("banner");
  banner.style.backgroundImage = `linear-gradient(rgba(0,0,0,0.4),rgba(0,0,0,0.4)),url('/static/${data[3]}'`;

  var name = document.getElementById("name");
  name.innerHTML = data[2];

  var price = document.getElementById("price");
  var ext = "";
  if(data[7]==1 || data[7]==true){
    ext="Per Hour";
  }
  price.innerHTML = `Price: $${data[5]} ${ext}`;
  var desc = document.getElementById("desc");
  desc.innerHTML = data[6];

  //seller section
  var seller = document.getElementById("seller");
  seller.setAttribute("onclick",`location.href='/profile/${data[10]}'`)
  var pfp = document.getElementById("sellerpfp");
  pfp.setAttribute("src",`/static/${data[11]}`);
  var un = document.getElementById("sellerun");
  un.innerHTML = data[10];
}