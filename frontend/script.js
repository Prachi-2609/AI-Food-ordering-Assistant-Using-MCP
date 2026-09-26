const SESSION_ID = "session_" + Math.random().toString(36).substr(2, 9);

// 1. Global Prevention: Kisi bhi tarah ke default form submit ko block karne ke liye
window.addEventListener("submit", function(e) {
    e.preventDefault();
    return false;
}, true);

// 2. Handle Initialization & Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    // A. Enter Key Support (Strict Logic to prevent refresh)
    const inputField = document.getElementById("prompt");
    if (inputField) {
        inputField.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault(); 
                sendPrompt();
            }
        });
    }

    // B. UPI ID Hide/Show Logic
    const paymentSelect = document.getElementById('orderPayment');
    const upiContainer = document.getElementById('upiIdContainer');
    
    if (paymentSelect && upiContainer) {
        upiContainer.style.display = 'none';
        paymentSelect.addEventListener('change', function() {
            if (this.value === 'UPI') {
                upiContainer.style.display = 'block';
            } else {
                upiContainer.style.display = 'none';
            }
        });
    }
});

// 3. Core Chat Logic
async function sendPrompt(e) {
    if (e) e.preventDefault();
    if (window.event) window.event.preventDefault();

    const promptBox = document.getElementById("prompt");
    const prompt = promptBox.value.trim();
    if (!prompt) return false;

    appendMessage("user", prompt);
    promptBox.value = "";
    
    const loadingId = appendMessage("bot", "⏳ Thinking...");

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: prompt, session_id: SESSION_ID }),
        });
        
        const data = await response.json();
        updateMessage(loadingId, data.reply || data.response);
    } catch (err) {
        updateMessage(loadingId, "Connection error. Check backend.");
    }
    
    return false; 
}

// 4. Checkout Modal Logic
async function openCheckoutModal() {
    try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: "view cart",
                session_id: SESSION_ID
            })
        });

        const data = await response.json();

        const status = data.reply || data.response || "";

        // Check if cart is empty
        if (status.toLowerCase().includes("cart is empty")) {
            alert("Your cart is empty! Add some items first.");
            return;
        }

        // Show actual cart contents
        document.getElementById("cartPreview").innerText = status;

        // Open checkout modal
        document.getElementById("checkoutModal").style.display = "block";

    } catch (e) {
        alert("Server error. Please try again.");
    }
}

function closeModal() { 
    document.getElementById('checkoutModal').style.display = 'none'; 
}

// 5. Final Order Submission (FIXED: Strict Prevention of Reload)
async function submitFinalOrder(e) {
    if (e) e.preventDefault();
    if (window.event) window.event.preventDefault();

    const address = document.getElementById('orderAddress').value;
    const phone = document.getElementById('orderPhone').value;
    const payment = document.getElementById('orderPayment').value;
    const upiId = document.getElementById('upiId') ? document.getElementById('upiId').value : "";

    if (!address) { 
        alert("Please enter valid address."); 
        return false; 
    }

    const phoneRegex = /^[0-9]{10}$/; 
    if (!phoneRegex.test(phone)) {
        alert("Invalid number! Please enter a valid 10-digit phone number.");
        return false;
    }

    // 3. UPI Check (Only if UPI is selected)
    if (payment === 'UPI' && !upiId) {
        alert("Please enter your UPI ID.");
        return false;
    }

    const finalPayment = payment === 'UPI' ? `UPI (${upiId})` : payment;

    try {
        const response = await fetch('http://127.0.0.1:8000/order/place', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                address: address, 
                phone: phone, 
                payment_method: finalPayment 
            })
        });

        if (response.ok) {
            alert("Order placed Successfully!"); 
            closeModal();
            // location.reload() hata diya taaki refresh na ho
            appendMessage("bot", "🎉 Your order has been placed! I've cleared your cart. Anything else you'd like to do?");
        } else {
            alert("Error placing order. Please try again.");
        }
    } catch (error) {
        alert("Connection failed.");
    }
    return false;
}

// 6. UI Helpers
let msgCounter = 0;

function appendMessage(role, text) {
    const chat = document.getElementById("chat");
    if (!chat) return;
    const id = "msg_" + (++msgCounter);
    const wrapper = document.createElement("div");
    wrapper.className = role; 
    wrapper.id = id;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    // Checks if text is from bot to parse Markdown (marked.js)
    bubble.innerHTML = role === "bot" ? marked.parse(text) : escapeHtml(text);

    wrapper.appendChild(bubble);
    chat.appendChild(wrapper);
    chat.scrollTop = chat.scrollHeight;
    return id;
}

function updateMessage(id, text) {
    const wrapper = document.getElementById(id);
    if (wrapper) {
        wrapper.querySelector(".bubble").innerHTML = marked.parse(text);
        const chat = document.getElementById("chat");
        chat.scrollTop = chat.scrollHeight;
    }
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}