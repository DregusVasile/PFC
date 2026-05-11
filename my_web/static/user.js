const currentUser = localStorage.getItem("currentUser") || "Guest";
const DEFAULT_PROFILE = {
  name: "Nume Utilizator",
  phone: "0745267813",
  email: "email@gamil.com",
  country: "O țară",
  locality: "O localitate",
  avatar: "",
  yourProductsBadge: "",
  cartProductsBadge: ""
};

let categories = [];
let uploadTarget = null;

function getProfile() {
  return {
    name: localStorage.getItem("profileName") || currentUser,
    phone: localStorage.getItem("profilePhone") || DEFAULT_PROFILE.phone,
    email: localStorage.getItem("profileEmail") || DEFAULT_PROFILE.email,
    country: localStorage.getItem("profileCountry") || DEFAULT_PROFILE.country,
    locality: localStorage.getItem("profileLocality") || DEFAULT_PROFILE.locality,
    avatar: localStorage.getItem("profileAvatar") || DEFAULT_PROFILE.avatar,
    yourProductsBadge: localStorage.getItem("badgeYourProducts") || DEFAULT_PROFILE.yourProductsBadge,
    cartProductsBadge: localStorage.getItem("badgeCartProducts") || DEFAULT_PROFILE.cartProductsBadge
  };
}

function saveProfile(profile) {
  localStorage.setItem("profileName", profile.name);
  localStorage.setItem("profilePhone", profile.phone);
  localStorage.setItem("profileEmail", profile.email);
  localStorage.setItem("profileCountry", profile.country);
  localStorage.setItem("profileLocality", profile.locality);
  if (profile.avatar !== undefined) {
    localStorage.setItem("profileAvatar", profile.avatar);
  }
  if (profile.yourProductsBadge !== undefined) {
    localStorage.setItem("badgeYourProducts", profile.yourProductsBadge);
  }
  if (profile.cartProductsBadge !== undefined) {
    localStorage.setItem("badgeCartProducts", profile.cartProductsBadge);
  }
}

function renderProfile() {
  const profile = getProfile();
  const avatar = document.getElementById("avatarCircle");

  document.getElementById("displayName").innerText = currentUser === "Guest" ? "Nume Utilizator" : currentUser;
  document.getElementById("profileUsername").innerText = currentUser === "Guest" ? "@Guest" : `@${currentUser}`;

  if (profile.avatar) {
    avatar.style.backgroundImage = `url('${profile.avatar}')`;
    avatar.textContent = "";
  } else {
    avatar.style.backgroundImage = "";
    avatar.textContent = currentUser === "Guest" ? "U" : currentUser.charAt(0).toUpperCase();
  }

  document.getElementById("phoneText").innerText = profile.phone;
  document.getElementById("emailText").innerText = profile.email;
  document.getElementById("countryText").innerText = profile.country;
  document.getElementById("localityText").innerText = profile.locality;
  document.getElementById("nameText").innerText = profile.name;

  document.getElementById("nameInput").value = profile.name;
  document.getElementById("phoneInput").value = profile.phone;
  document.getElementById("emailInput").value = profile.email;
  document.getElementById("countryInput").value = profile.country;
  document.getElementById("localityInput").value = profile.locality;

  const yourBadge = document.getElementById("yourProductsBadge");
  const cartBadge = document.getElementById("cartProductsBadge");
  if (profile.yourProductsBadge) {
    yourBadge.innerHTML = `<img src="${profile.yourProductsBadge}" alt="Badge" />`;
  } else {
    yourBadge.innerHTML = "";
  }
  if (profile.cartProductsBadge) {
    cartBadge.innerHTML = `<img src="${profile.cartProductsBadge}" alt="Badge" />`;
  } else {
    cartBadge.innerHTML = "";
  }
}

function toggleEdit() {
  const details = document.getElementById("profileDetails");
  const editBtn = document.getElementById("editBtn");
  const isEditing = details.classList.toggle("editing");

  if (!isEditing) {
    const profile = {
      name: document.getElementById("nameInput").value.trim() || DEFAULT_PROFILE.name,
      phone: document.getElementById("phoneInput").value.trim() || DEFAULT_PROFILE.phone,
      email: document.getElementById("emailInput").value.trim() || DEFAULT_PROFILE.email,
      country: document.getElementById("countryInput").value.trim() || DEFAULT_PROFILE.country,
      locality: document.getElementById("localityInput").value.trim() || DEFAULT_PROFILE.locality,
      avatar: getProfile().avatar,
      yourProductsBadge: getProfile().yourProductsBadge,
      cartProductsBadge: getProfile().cartProductsBadge
    };
    saveProfile(profile);
    renderProfile();
    // Update seller info if product page is open
    if (typeof updateSellerInfo === 'function') {
      updateSellerInfo();
    }
    editBtn.innerText = "Editează";
  } else {
    editBtn.innerText = "Salvează";
    document.getElementById("nameInput").focus();
  }
}

function editBadgeIfAdmin(type) {
  const isAdmin = localStorage.getItem("currentUserIsAdmin") === "true";
  if (type === "avatar") {
    // Allow avatar editing for all users
    openImageModal(type);
  } else if (!isAdmin) {
    alert("Doar adminul poate modifica insignele.");
    return;
  } else {
    openImageModal(type);
  }
}

function openImageModal(type) {
  uploadTarget = type;
  const title = document.getElementById("imageModalTitle");
  title.innerText = type === "avatar" ? "Încarcă poza de profil" : "Încarcă un PNG pentru emblemă";
  document.getElementById("imageFileInput").value = "";
  document.getElementById("imagePreview").innerHTML = "";
  document.getElementById("imageModal").classList.remove("hidden");
}

function closeImageModal() {
  uploadTarget = null;
  document.getElementById("imageModal").classList.add("hidden");
}

function saveImageSelection() {
  const input = document.getElementById("imageFileInput");
  if (!input.files.length) {
    alert("Alege un fișier PNG.");
    return;
  }

  const file = input.files[0];
  if (file.type !== "image/png") {
    alert("Doar fișiere PNG sunt permise.");
    return;
  }

  const reader = new FileReader();
  reader.onload = function () {
    const imageData = reader.result;
    const profile = getProfile();

    if (uploadTarget === "avatar") {
      profile.avatar = imageData;
    } else if (uploadTarget === "yourProducts") {
      profile.yourProductsBadge = imageData;
    } else if (uploadTarget === "cartProducts") {
      profile.cartProductsBadge = imageData;
    }

    saveProfile(profile);
    renderProfile();
    closeImageModal();
  };
  reader.readAsDataURL(file);
}

function renderCategoryOptions() {
  const container = document.getElementById("categoryOptions");
  container.innerHTML = "";

  categories.forEach(cat => {
    const option = document.createElement("div");
    option.className = "category-option";
    option.innerText = cat;
    option.onclick = () => selectCategory(cat);
    container.appendChild(option);
  });

  const createNew = document.createElement("div");
  createNew.className = "category-option category-option-new";
  createNew.innerText = "Categorie nouă";
  createNew.onclick = () => {
    document.getElementById("productCategory").value = "";
    document.getElementById("productCategory").focus();
    hideCategoryOptions();
  };
  container.appendChild(createNew);
}

function showCategoryOptions() {
  document.getElementById("categoryOptions").classList.add("visible");
}

function hideCategoryOptions() {
  document.getElementById("categoryOptions").classList.remove("visible");
}

function selectCategory(cat) {
  document.getElementById("productCategory").value = cat;
  hideCategoryOptions();
}

async function loadCategories() {
  try {
    const response = await fetch("/categories");
    categories = await response.json();
    renderCategoryOptions();
  } catch (error) {
    console.error("Unable to load categories", error);
  }
}

async function updateCounts() {
  try {
    const cartRes = await fetch("/get-cart");
    const cart = await cartRes.json();
    document.getElementById("cartProductsCount").innerText = cart.length;
  } catch (error) {
    console.error("Unable to load cart count", error);
    document.getElementById("cartProductsCount").innerText = 0;
  }

  try {
    const productsRes = await fetch("/my-products-json");
    const products = await productsRes.json();
    // Count products where seller matches current user
    const userProducts = products.filter(p => p.seller === currentUser);
    document.getElementById("yourProductsCount").innerText = userProducts.length;
  } catch (error) {
    console.error("Unable to load your products count", error);
    document.getElementById("yourProductsCount").innerText = 0;
  }
}

function scrollToAddProduct() {
  document.getElementById("addProductSection").scrollIntoView({ behavior: "smooth" });
}

async function addProducts() {
  const name = document.getElementById("productName").value.trim();
  const priceValue = parseInt(document.getElementById("productPrice").value.trim(), 10);
  const image = document.getElementById("productImage").value.trim();
  const category = document.getElementById("productCategory").value.trim();
  const stockValue = parseInt(document.getElementById("productStock").value.trim(), 10);
  const description = document.getElementById("productDesc").value.trim();
  

  if (!name || !priceValue || !image || !category || !stockValue) {
    alert("Trebuie să completezi Nume produs, Preț, Imagine URL, Categorie și Nr. produse.");
    return;
  }

  if (isNaN(priceValue) || priceValue < 1) {
    alert("Prețul trebuie să fie un număr întreg mai mare decât 0.");
    return;
  }

  if (isNaN(stockValue) || stockValue < 1) {
    alert("Nr. produse trebuie să înceapă de la 1.");
    return;
  }

  const product = {
    name,
    price: priceValue,
    image,
    category,
    description,
    stock: stockValue,
    purchaseLimit: 1, // Default purchase limit
    seller: currentUser
  };

  try {
    const res = await fetch("/add-product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(product)
    });
    const data = await res.json();

    if (data.status === "ok") {
      alert("Produsul a fost adăugat!");
      window.location.href = "/shop";
    } else {
      alert("A apărut o eroare la adăugarea produsului.");
    }
  } catch (error) {
    console.error("Unable to add product", error);
    alert("A apărut o eroare la adăugarea produsului.");
  }
}

window.logout = function() {
  localStorage.clear();
  window.location.href = "/";
}

window.addEventListener("DOMContentLoaded", () => {
  renderProfile();
  loadCategories();
  updateCounts();

  document.addEventListener("click", event => {
    const categoryOptions = document.getElementById("categoryOptions");
    const categoryInput = document.getElementById("productCategory");
    if (!categoryOptions.contains(event.target) && event.target !== categoryInput) {
      hideCategoryOptions();
    }
  });
});
