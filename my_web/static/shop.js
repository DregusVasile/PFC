document.addEventListener("DOMContentLoaded", ()=>{

const CURRENCY = "RON"

const productsDiv = document.getElementById("products")
const searchInput = document.getElementById("search")
const cartCount = document.getElementById("cartCount")
const username = document.getElementById("username")

username.innerText = localStorage.getItem("currentUser") || "Guest"

/* PRODUSE */
let products = [
{
name:"Phone",
price:1500,
cat:"Electronics",
img:"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTvP9ILf5sFBTv5C2PxocHhNPBVL0qX2XzXdA&s"
},
{
name:"Sneakers",
price:500,
cat:"Clothing",
img:"https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcQzhT58jSwR0taqgXGBasuUDidQgdBCTZEKmLH7GVxNr--eU2wanZwzhMlZi_GBJ0ZHGnBTyeod79ZVw6KTmWbo736k4SJ0Tdk3romdz-3tUvxgQASOt31NES57wWFgnARXDvaPppz8P0s&usqp=CAc"
},
{
name:"Headphones",
price:320,
cat:"Electronics",
img:"https://sony.scene7.com/is/image/sonyglobalsolutions/Headphones_Product-finder_WH-1000XM6?$productFinder$&fmt=png-alpha"
},
{
name:"Chairs",
price:40,
cat:"Home",
img:"https://store.ashleyfurniture.ph/cdn/shop/files/D974-01-ANGLE-ALT-SW.jpg?v=1757064513"
},
{
name:"Watch",
price:300,
cat:"Electronics",
img:"https://www.sonatawatches.in/dw/image/v2/BKDD_PRD/on/demandware.static/-/Sites-titan-master-catalog/default/dw7b993993/images/Sonata/Catalog/7152QM01_1.jpg?sw=600&sh=600"
},
{name:"Jacket",
price:150,
cat:"Clothing",
img:"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTUjL7jlnPo6GVI-81B3BNl1OqBvJEhEdUzJQ&s"
}
]

window.openCart = function(){
const box = document.getElementById("cartBox")
const items = document.getElementById("cartItems")

box.style.display = box.style.display === "none" ? "block" : "none"

items.innerHTML=""

cart.forEach(p=>{
items.innerHTML += `
<p>${p.name} - ${p.price} ${CURRENCY}</p>
`
})
}
let selectedCategory = "All"
const categories = ["All", ...new Set(products.map(p=>p.cat))]
const categoryList = document.getElementById("categoryList")
const categoryBtn = document.getElementById("categoryBtn")

categories.forEach(c=>{
    const div = document.createElement("div")
    div.innerText = c

    div.onclick = ()=>{
        selectedCategory = c
        categoryBtn.innerText = c === "All" ? "Categories ▼" : c + " ▼"
        categoryList.style.display = "none"
        filterProducts()
    }

    categoryList.appendChild(div)
})
window.toggleCategories = function(){
    categoryList.style.display =
        categoryList.style.display === "flex" ? "none" : "flex"
}
function filterProducts(){
    let filtered = products

    if(selectedCategory !== "All"){
        filtered = filtered.filter(p=>p.cat === selectedCategory)
    }

    const text = searchInput.value.toLowerCase()
    filtered = filtered.filter(p=>p.name.toLowerCase().includes(text))

    render(filtered)
}



/* 🔥 GENEREAZĂ MULTE PRODUSE */
for(let i=1;i<301;i++){
products.push({
name:"Product "+i,
price:Math.floor(Math.random()*300+50),
img:"https://picsum.photos/200?random="+i
})
}

/* RENDER */
function render(list){
productsDiv.innerHTML=""

list.forEach(p=>{
productsDiv.innerHTML+=`
<div class="card">
<img src="${p.img}">
<h4>${p.name}</h4>

<div class="bottom">
<div class="price">${p.price} ${CURRENCY}</div>
<button onclick="addToCart(${list.indexOf(p)})">Add</button>

</div>

</div>
`
})
}

/* SEARCH */
window.search = function(){
    filterProducts()
}

/* CART */
{let cart = []
window.addToCart = function(index){
cart.push(products[index])
cartCount.innerText = cart.length
}
}

/* INIT */
render(products)

})
