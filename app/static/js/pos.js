var currentOrderId = null;
var currentOrderStatus = null;

document.addEventListener("DOMContentLoaded", function () {
  var itemsGrid = document.getElementById("items-grid");
  var cartItems = document.getElementById("cart-items");
  var cartTotals = document.getElementById("cart-totals");
  var orderInfo = document.getElementById("order-info");
  var newOrderBtn = document.getElementById("new-order-btn");
  var payBtn = document.getElementById("pay-btn");
  var activeOrdersList = document.getElementById("active-orders-list");

  if (!itemsGrid) return;

  itemsGrid.addEventListener("click", function (e) {
    var btn = e.target.closest(".item-btn");
    if (!btn) return;
    if (!currentOrderId) {
      alert("Please create a new order first.");
      return;
    }
    if (currentOrderStatus !== "open") {
      alert("This order is already " + currentOrderStatus + " and cannot be modified.");
      return;
    }
    addItemToOrder(btn.dataset.id);
  });

  document.querySelectorAll(".tab-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
      this.classList.add("active");
      var catId = this.dataset.category;
      document.querySelectorAll(".item-btn").forEach(function (item) {
        item.style.display = (!catId || item.dataset.category === catId) ? "" : "none";
      });
    });
  });

  var firstTab = document.querySelector(".tab-btn");
  if (firstTab) firstTab.click();

  newOrderBtn.addEventListener("click", function () {
    if (currentOrderId && currentOrderStatus === "open" && cartHasItems()) {
      if (!confirm("Discard current order and create a new one?")) return;
    }
    fetch("/pos/orders", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        currentOrderId = data.id;
        currentOrderStatus = "open";
        orderInfo.innerHTML = "<p><strong>Order:</strong> " + data.order_number + " <span class='status-open'>(open)</span></p>";
        payBtn.disabled = false;
        cartItems.innerHTML = "";
        cartTotals.innerHTML = "";
        updateCartToggleInfo(null);
        refreshActiveOrders();
      });
  });

  payBtn.addEventListener("click", function () {
    if (!currentOrderId || currentOrderStatus !== "open") return;
    document.getElementById("pay-order-id").value = currentOrderId;
    var numEl = document.querySelector("#order-info p strong");
    document.getElementById("pay-order-number").textContent = numEl ? numEl.nextSibling.textContent.trim() : "";
    var totalEl = document.querySelector(".cart-totals .total span");
    document.getElementById("pay-total").textContent = totalEl ? totalEl.textContent : "0.00";
    document.getElementById("pay-modal").style.display = "flex";
  });

  var payForm = document.getElementById("pay-form");
  if (payForm) {
    payForm.addEventListener("submit", function (e) {
      e.preventDefault();
      fetch("/pos/orders/" + document.getElementById("pay-order-id").value + "/pay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payment_type: document.getElementById("payment-type").value }),
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.success) {
            alert("Payment recorded.");
            closePayModal();
            resetCart();
            refreshActiveOrders();
          } else {
            alert("Error: " + (data.error || "Unknown"));
          }
        });
    });
  }

  // Event delegation: order link clicks
  if (activeOrdersList) {
    activeOrdersList.addEventListener("click", function (e) {
      var link = e.target.closest(".order-link");
      if (link) {
        e.preventDefault();
        loadOrder(link.dataset.orderId);
        return;
      }
      var cancelBtn = e.target.closest(".cancel-order-btn");
      if (cancelBtn) {
        e.stopPropagation();
        if (!confirm("Cancel this order?")) return;
        cancelOrderAjax(cancelBtn.dataset.orderId);
      }
    });
  }

  // Event delegation: cart item remove clicks
  if (cartItems) {
    cartItems.addEventListener("click", function (e) {
      var removeBtn = e.target.closest(".cart-item-remove");
      if (!removeBtn) return;
      if (!currentOrderId || currentOrderStatus !== "open") return;
      var itemId = removeBtn.dataset.itemId;
      fetch("/pos/orders/" + currentOrderId + "/items/" + itemId, { method: "DELETE" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.success) {
            renderOrder(data.order);
          } else {
            alert("Error: " + (data.error || "Unknown"));
          }
        });
    });
  }
});

function cancelOrderAjax(orderId) {
  fetch("/pos/orders/" + orderId + "/cancel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        if (currentOrderId === orderId) resetCart();
        refreshActiveOrders();
      } else {
        alert("Error: " + (data.error || "Unknown"));
      }
    })
    .catch(function () {
      location.reload();
    });
}

function cartHasItems() {
  var el = document.getElementById("cart-items");
  return el && el.children.length > 0;
}

function refreshActiveOrders() {
  fetch("/pos/orders/active/json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (!data.success) return;
      var list = document.getElementById("active-orders-list");
      if (!list) return;
      list.innerHTML = data.orders
        .map(function (o) {
          return '<li class="active-order-item">' +
            '<a href="#" class="order-link" data-order-id="' + o.id + '">' +
            o.order_number + " - $" + o.total.toFixed(2) + "</a>" +
            '<button class="cancel-order-btn btn btn-sm btn-danger" data-order-id="' + o.id + '" title="Cancel order">&times;</button>' +
            "</li>";
        })
        .join("");
    });
}

function addItemToOrder(menuItemId) {
  fetch("/pos/orders/" + currentOrderId + "/items", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ menu_item_id: menuItemId, quantity: 1 }),
  })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        renderOrder(data.order);
      } else {
        alert("Error: " + (data.error || "Unknown"));
      }
    });
}

function loadOrder(orderId) {
  fetch("/pos/orders/" + orderId + "/json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.success) {
        currentOrderId = orderId;
        currentOrderStatus = data.order.status;
        document.getElementById("pay-btn").disabled = (data.order.status !== "open");
        renderOrder(data.order);
      } else {
        alert("Error: " + (data.error || "Unknown"));
      }
    });
}

function updateCartToggleInfo(order) {
  var infoEl = document.getElementById("cartToggleInfo");
  var countEl = document.getElementById("cartToggleCount");
  if (!infoEl || !countEl) return;
  if (!order || !order.items || order.items.length === 0) {
    infoEl.textContent = "No active order";
    countEl.textContent = "0 items";
    return;
  }
  infoEl.textContent = "$" + order.total.toFixed(2);
  var n = order.items.length;
  countEl.textContent = n + " item" + (n !== 1 ? "s" : "");
}

function renderOrder(order) {
  var cartItems = document.getElementById("cart-items");
  var cartTotals = document.getElementById("cart-totals");
  var orderInfo = document.getElementById("order-info");

  var statusLabel = order.status === "open"
    ? "<span class='status-open'>(open)</span>"
    : "<span class='status-closed'>(" + order.status + ")</span>";
  orderInfo.innerHTML = "<p><strong>Order:</strong> " + order.order_number + " " + statusLabel + "</p>";

  if (order.status !== "open") {
    cartItems.innerHTML = "<p style='color:#64748b;text-align:center;padding:1rem;'>This order is <strong>" + order.status + "</strong>. No further changes allowed.</p>";
    cartTotals.innerHTML =
      "<p><span>Subtotal</span><span>$" + order.subtotal.toFixed(2) + "</span></p>" +
      "<p><span>Tax</span><span>$" + order.tax.toFixed(2) + "</span></p>" +
      '<p class="total"><span>Total</span><span>$' + order.total.toFixed(2) + "</span></p>";
    updateCartToggleInfo(order);
    return;
  }

  cartItems.innerHTML = order.items
    .map(function (item) {
      return '<div class="cart-item">' +
        '<span class="cart-item-name">' + item.name + "</span>" +
        '<span class="cart-item-qty">' + item.quantity + "</span>" +
        '<span class="cart-item-price">$' + item.line_total.toFixed(2) + "</span>" +
        '<button class="cart-item-remove" data-item-id="' + item.id + '">&times;</button>' +
        "</div>";
    })
    .join("");

  cartTotals.innerHTML =
    "<p><span>Subtotal</span><span>$" + order.subtotal.toFixed(2) + "</span></p>" +
    "<p><span>Tax</span><span>$" + order.tax.toFixed(2) + "</span></p>" +
    '<p class="total"><span>Total</span><span>$' + order.total.toFixed(2) + "</span></p>";

  updateCartToggleInfo(order);
}

function resetCart() {
  currentOrderId = null;
  currentOrderStatus = null;
  document.getElementById("order-info").innerHTML = "<p>No active order selected.</p>";
  document.getElementById("cart-items").innerHTML = "";
  document.getElementById("cart-totals").innerHTML = "";
  document.getElementById("pay-btn").disabled = true;
  updateCartToggleInfo(null);
}

function closePayModal() {
  document.getElementById("pay-modal").style.display = "none";
}
