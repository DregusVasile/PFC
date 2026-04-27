async function getCart(){
  console.log('getCart: fetching from /get-cart');
  const res = await fetch('/get-cart');
  const data = await res.json();
  console.log('getCart response:', JSON.stringify(data));
  return data;
}

async function saveCart(cart){
  // Not needed, since we save on add
}

async function addToCart(product){
  console.log('addToCart called with:', product);
  console.log('Product JSON:', JSON.stringify(product));
  try {
    const response = await fetch('/add-to-cart', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(product)
    });
    console.log('Fetch response:', response.status, response.ok);
    const responseData = await response.json();
    console.log('Server response:', JSON.stringify(responseData));
    if (response.ok) {
      console.log('Calling updateCartUI...');
      await updateCartUI();
      console.log('updateCartUI done');
    } else {
      alert('Failed to add to cart');
    }
    return response;
  } catch (error) {
    console.error('Error adding to cart:', error);
    alert('Error adding to cart: ' + error.message);
  }
}

async function updateCartUI(){
  try {
    console.log('updateCartUI: fetching cart from /get-cart');
    const cart = await getCart();
    console.log('Cart contents:', JSON.stringify(cart));
    const count = cart.length;
    console.log('Cart count:', count);
    document.querySelectorAll("#cartCount").forEach(el=>{
      el.innerText = count;
    });
  } catch (e) {
    console.error('Failed to update cart UI', e);
  }
}

document.addEventListener("DOMContentLoaded", updateCartUI);
