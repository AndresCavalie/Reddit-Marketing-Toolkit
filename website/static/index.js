let searchbox = document.getElementById('searchBox');
searchbox.style.display="none";

function deleteSearch(searchId) {
  fetch("/delete-search", {
    method: "POST",
    body: JSON.stringify({ searchId: searchId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}



function newSearch(){
  console.log("NOICE")
  if (searchbox.style.display == "none"){
    searchbox.style.display="block"
  }
  else{
    searchbox.style.display="none"
  }
    
  
 // box.value = \"<h1>NICE</h1>\"
}
function backHome(){
  
    window.location.href = "/";
}


function deletePost(postId) {
  fetch("/delete-post", {
    method: "POST",
    body: JSON.stringify({ postId: postId }),
  }).then((_res) => {
    window.location.href = "/searches";
  });
}

function enterSearch(searchId){
  fetch("/enter-search", {
    method: "POST",
    body: JSON.stringify({searchId:searchId}),
  }).then((_res) => {
    window.location.href = "/searches";
  });
  console.log("HIT")
}