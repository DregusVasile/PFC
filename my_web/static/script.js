let tracking = true
const radius = 10

document.addEventListener("mousemove", e=>{
if(!tracking) return
moveEyes("char1", e)
moveEyes("char2", e)
moveEyes("char3", e)
})

function moveEyes(id,e){
const el=document.getElementById(id)
if(!el) return

const eyes=el.querySelectorAll(".eye")
const r=el.getBoundingClientRect()

const cx=r.left+r.width/2
const cy=r.top+r.height/2

let dx=e.clientX-cx
let dy=e.clientY-cy

const dist=Math.sqrt(dx*dx+dy*dy)

if(dist>radius){
dx=dx/dist*radius
dy=dy/dist*radius
}

eyes.forEach(eye=>{
eye.style.transform=`translate(${dx}px,${dy}px)`
})
}

function lookAway(){
tracking=false
document.querySelectorAll(".eye").forEach(e=>{
e.style.transform="translate(0,-8px)"
})
setTimeout(()=>tracking=true,2500)
}

function togglePassword(id){
const input=document.getElementById(id)
input.type=input.type==="password"?"text":"password"
lookAway()
}

/* SWITCH */
function showSignup(){
document.getElementById("loginBox").style.display="none"
document.getElementById("signupBox").style.display="block"
}

function showLogin(){
document.querySelector(".login-box").style.display="block"
document.getElementById("signupBox").style.display="none"
}

/* AUTH */
async function signup(){
  const u = document.getElementById("signUser").value;
  const p = document.getElementById("signPass").value;
  const c = document.getElementById("confirmPass").value;

  if(!u || !p || !c){
    alert("Complete all fields");
    return;
  }

  if(p !== c){
    alert("Passwords do not match");
    return;
  }

  const res = await fetch("/signup", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({username:u, password:p})
  });

  const data = await res.json();

  if(data.status === "ok"){
    alert("Account created!");
    showLogin();
  } else {
    alert("User already exists");
  }
}

async function login(){
  const u = document.getElementById("loginUser").value;
  const p = document.getElementById("loginPass").value;

  const res = await fetch("/login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({username:u, password:p})
  });

  const data = await res.json();

  if(data.status === "ok"){
    localStorage.setItem("currentUser", u);
    localStorage.setItem("currentUserIsAdmin", data.isAdmin ? "true" : "false");
    window.location.href = "/shop";
  } else {
    alert("Wrong credentials");
  }
}