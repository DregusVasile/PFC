document.addEventListener("DOMContentLoaded", () => {

const CURRENCY = "RON";
const PRODUCTS_PER_PAGE = 36;

const productsDiv = document.getElementById("products");
const categoryList = document.getElementById("categoryList");
const cartCount = document.getElementById("cartCount");
const username = document.getElementById("username");

document.getElementById("username").innerText =
  localStorage.getItem("currentUser") || "Guest";


username.innerText = localStorage.getItem("currentUser") || "Guest";

let allProducts = [];
let filteredProducts = [];
let currentPage = 1;
let currentCategory = "All";

/* ================= LOAD JSON ================= */
async function loadAllProducts() {
  const res = await fetch("/all-products-json");
  const data = await res.json();

  allProducts = data;

  setupCategories();   // 🔥 IMPORTANT
  applyFilter("All");  // 🔥 IMPORTANT
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

window.toggleCategories = function() {
  const list = document.getElementById("categoryList");
  list.style.display = list.style.display === "flex" ? "none" : "flex";
}

function getRecommended(product) {

  const sameCategory = allProducts.filter(p => p.category === product.category).slice(0,5);

  const related = allProducts.filter(p =>
    p.name.toLowerCase().includes("laptop") && product.name.toLowerCase().includes("laptop")
  ).slice(0,5);

  const randomSameCategory = allProducts
    .filter(p => p.category === product.category)
    .sort(() => 0.5 - Math.random())
    .slice(0,5);

  const newest = [...allProducts].slice(-5);

  return [
    ...sameCategory,
    ...related,
    ...randomSameCategory,
    ...newest
  ];
}

window.addToCartItem = async function(event, product) {
  event.stopPropagation();
  await addToCart(product);
}

function selectCategory(cat) {
  currentCategory = cat;
  currentPage = 1;
  applyFilter(cat);
  document.getElementById("categoryList").style.display = "none";
}

function applyFilter(cat) {
  if (cat === "All") {
  filteredProducts = allProducts;
} else {
  filteredProducts = allProducts.filter(p =>
    p.category === cat || p.subcategory === cat
  );
}

  currentPage = 1;
  loadPage(1);
  updateArrows();
}



/* ================= PAGINATION ================= */
function loadPage(page) {
  const start = (page - 1) * PRODUCTS_PER_PAGE;
  const end = start + PRODUCTS_PER_PAGE;

  const items = filteredProducts.slice(start, end);

  renderProducts(items);
  updateArrows();
}

window.nextPage = function () {
  const maxPage = Math.ceil(filteredProducts.length / PRODUCTS_PER_PAGE);

  if (currentPage < maxPage) {
    currentPage++;
    loadPage(currentPage);
  }
}

window.openUser = function() {
  window.location.href = "/user";
}

window.logout = function() {
  localStorage.clear();
  window.location.href = "/";
}

function normalize(text) {
  return text
    .toLowerCase()
    .replace(/ă/g, "a")
    .replace(/â/g, "a")
    .replace(/î/g, "i")
    .replace(/ș/g, "s")
    .replace(/ț/g, "t");
}

window.search = function () {
  const value = normalize(document.getElementById("search").value);

  const filtered = allProducts.filter(p =>
    normalize(p.name).includes(value)
  );

  filteredProducts = filtered;
  currentPage = 1;
  loadPage(1);
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
  productsDiv.innerHTML = ""; // 🔥 IMPORTANT

  items.forEach(p => {
    const card = document.createElement("div");
    card.className = "card";

    const img = document.createElement("img");
    img.src = p.image;
    img.onerror = () => img.src = 'https://via.placeholder.com/150';

    const title = document.createElement("h4");
    title.innerText = p.name;

    const price = document.createElement("div");
    price.className = "price";
    price.innerText = `${p.price} ${CURRENCY}`;

    const button = document.createElement("button");
    button.innerText = "Add";
    button.addEventListener("click", async event => {
      console.log('Add button clicked for product:', p);
      event.stopPropagation();
      await addToCart(p);
    });

    const priceButtonContainer = document.createElement("div");
    priceButtonContainer.className = "price-button-row";
    priceButtonContainer.appendChild(price);
    priceButtonContainer.appendChild(button);

    const textContent = document.createElement("div");
    textContent.className = "text-content";
    textContent.appendChild(title);
    textContent.appendChild(priceButtonContainer);

    card.appendChild(img);
    card.appendChild(textContent);

    card.addEventListener("click", () => {
      localStorage.setItem("selectedProduct", JSON.stringify(p));
      window.location.href = "/product";
    });

    productsDiv.appendChild(card);
  });
}

/* ================= INIT ================= */
loadAllProducts();

});