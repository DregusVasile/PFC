async function getCart(){
  const res = await fetch('/get-cart');
  return await res.json();
}

async function addToCart(product){
  try {
    const cartItem = {
      product_id: product.id,
      name: product.name,
      price: product.price,
      quantity: 1,
      source: product.source || 'shop'
    };
    
    const response = await fetch('/add-to-cart', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(cartItem)
    });

    if (response.ok) {
      await updateCartUI();
    } else {
      alert('Failed to add to cart');
    }

    return response;
  } catch (error) {
    console.error('Error adding to cart:', error);
    alert('Error adding to cart: ' + error.message);
  }
}

async function removeFromCart(index){
  try {
    const res = await fetch('/remove-from-cart', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ index })
    });

    if (res.ok) {
      await updateCartUI();
      if (document.getElementById('cartPopup')?.classList.contains('visible')) {
        await refreshCartPopup();
      }
    }
  } catch (error) {
    console.error('Error removing item from cart:', error);
  }
}

async function updateCartUI(){
  try {
    const cart = await getCart();
    const count = cart.length;
    document.querySelectorAll('#cartCount').forEach(el => {
      el.innerText = count;
    });
    if (document.getElementById('cartPopup')?.classList.contains('visible')) {
      await refreshCartPopup();
    }
  } catch (e) {
    console.error('Failed to update cart UI', e);
  }
}

function createCartPopup(){
  if (document.getElementById('cartPopup')) return;

  const popup = document.createElement('div');
  popup.id = 'cartPopup';
  popup.className = 'cart-popup';
  popup.innerHTML = `
    <div class="cart-popup-header">
      <h3>Your Cart</h3>
      <button class="cart-popup-close" onclick="toggleCartPopup()">×</button>
    </div>
    <div class="cart-total-section">
      <div id="cartPopupTotal" class="cart-total">Total: 0 RON</div>
      <button class="buy-all-cart-btn" onclick="buyAllFromCart()">Buy All</button>
    </div>
    <div id="cartPopupItems" class="cart-items"></div>
  `;
  document.body.appendChild(popup);
}

function renderCartPopup(cart){
  const itemsContainer = document.getElementById('cartPopupItems');
  const totalLabel = document.getElementById('cartPopupTotal');

  if (!itemsContainer || !totalLabel) return;

  let total = 0;
  itemsContainer.innerHTML = '';

  if (!cart.length) {
    itemsContainer.innerHTML = '<div class="cart-empty">Cosul este gol.</div>';
    totalLabel.innerText = 'Total: 0 RON';
    return;
  }

  cart.forEach((item, index) => {
    const price = Number(item.price) || 0;
    total += price;

    const itemDiv = document.createElement('div');
    itemDiv.className = 'cart-item';

    itemDiv.innerHTML = `
      <div class="item-name">${item.name || 'Produs'}</div>
      <div class="item-price">${price.toFixed(2)} RON</div>
      <div class="item-actions">
        <span>${item.category || ''}</span>
        <button onclick="removeFromCart(${index})">Șterge</button>
      </div>
    `;

    itemsContainer.appendChild(itemDiv);
  });

  totalLabel.innerText = `Total: ${total.toFixed(2)} RON`;
}

async function refreshCartPopup(){
  const cart = await getCart();
  renderCartPopup(cart);
}

async function buyAllFromCart(){
  const cart = await getCart();
  
  if (!cart.length) {
    alert("Cosul este gol.");
    return;
  }

  const currentUser = localStorage.getItem("currentUser") || "Guest";
  const profileEmail = localStorage.getItem("profileEmail") || "email@gmail.com";
  const profileName = localStorage.getItem("profileName") || currentUser;

  try {
    for (const item of cart) {
      const response = await fetch("/buy-all", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
          user: currentUser,
          userId: profileName,
          email: profileEmail,
          quantity: 1,
          product: item
        })
      });

      const data = await response.json();
      if (data.status !== "ok") {
        alert("Eroare la cumpărarea: " + item.name);
        return;
      }
    }

    alert("Toate produsele au fost cumpărate cu succes!");
    
    // Clear cart
    await fetch("/clear-cart", {
      method: "POST",
      headers: {"Content-Type":"application/json"}
    });

    await updateCartUI();
    await refreshCartPopup();
    
  } catch (error) {
    console.error("Error buying cart items:", error);
    alert("Eroare la cumpărare: " + error.message);
  }
}

window.toggleCartPopup = async function(){
  createCartPopup();
  const popup = document.getElementById('cartPopup');
  if (!popup) return;

  const isOpen = popup.classList.toggle('visible');
  if (isOpen) {
    await refreshCartPopup();
  }
};

window.addEventListener('DOMContentLoaded', () => {
  updateCartUI();
  createCartPopup();
});