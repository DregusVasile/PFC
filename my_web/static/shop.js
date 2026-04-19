document.addEventListener("DOMContentLoaded", () => {

const CURRENCY = "RON";
const PRODUCTS_PER_PAGE = 42;

const productsDiv = document.getElementById("products");
const categoryList = document.getElementById("categoryList");
const cartCount = document.getElementById("cartCount");
const username = document.getElementById("username");

username.innerText = localStorage.getItem("currentUser") || "Guest";

let allProducts = [];
let filteredProducts = [];
let currentPage = 1;
let currentCategory = "All";

/* ================= LOAD JSON ================= */
async function loadAllProducts() {
  try {
    const res = await fetch("/products-json");
    allProducts = await res.json();

    setupCategories();
    applyFilter("All");
  } catch (err) {
    console.error("Eroare la load JSON:", err);
  }
}

/* ================= CATEGORIES ================= */
function setupCategories() {
  const categories = ["All", ...new Set(allProducts.map(p => p.category))];

  categoryList.innerHTML = "";

  categories.forEach(cat => {
    const div = document.createElement("div");
    div.innerText = cat;
    div.onclick = () => selectCategory(cat);
    categoryList.appendChild(div);
  });
}

window.toggleCategories = function () {
  categoryList.style.display =
    categoryList.style.display === "block" ? "none" : "block";
}

function selectCategory(cat) {
  currentCategory = cat;
  currentPage = 1;
  applyFilter(cat);
}

function applyFilter(cat) {
  if (cat === "All") {
    filteredProducts = allProducts;
  } else {
    filteredProducts = allProducts.filter(p => p.category === cat);
  }

  loadPage(1);
  updateArrows();
}

/* ================= PAGINATION ================= */
function loadPage(page) {
  const start = (page - 1) * PRODUCTS_PER_PAGE;
  const end = start + PRODUCTS_PER_PAGE;

  const items = filteredProducts.slice(start, end);

  renderProducts(items);
}

window.nextPage = function () {
  const maxPage = Math.ceil(filteredProducts.length / PRODUCTS_PER_PAGE);

  if (currentPage < maxPage) {
    currentPage++;
    loadPage(currentPage);
  }
}

window.prevPage = function () {
  if (currentPage > 1) {
    currentPage--;
    loadPage(currentPage);
  }
}

function updateArrows() {
  const maxPage = Math.ceil(filteredProducts.length / PRODUCTS_PER_PAGE);

  document.querySelector(".left-btn").style.opacity = currentPage === 1 ? 0.3 : 1;
  document.querySelector(".right-btn").style.opacity = currentPage === maxPage ? 0.3 : 1;
}

/* ================= RENDER ================= */
function renderProducts(items) {
  productsDiv.innerHTML = "";

  items.forEach(p => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <img src="${p.image}" onerror="this.src='https://via.placeholder.com/150'">
      <h4>${p.name}</h4>
      <div class="bottom">
        <div class="price">${p.price} ${CURRENCY}</div>
        <button>Add</button>
      </div>
    `;

    productsDiv.appendChild(card);
  });
}

/* ================= INIT ================= */
loadAllProducts();

});