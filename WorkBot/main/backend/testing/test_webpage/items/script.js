let items = [];
let sortAsc = true; // toggle state

window.onload = () => {
  fetch('items.json')
    .then(res => res.json())
    .then(data => {
      items = data;
      renderItems(data);
    })
    .catch(err => {
      console.error("Error loading JSON:", err);
      document.querySelector("#itemsTable tbody").innerHTML = `<tr><td colspan="2">Failed to load items.</td></tr>`;
    });
};

function renderItems(data) {
  const tbody = document.querySelector("#itemsTable tbody");
  tbody.innerHTML = "";

  data.forEach(item => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td><a onclick="openModal('${item.id}')">${item.name}</a></td>
      <td><button onclick="openModal('${item.id}')">View Vendors</button></td>
    `;

    tbody.appendChild(tr);
  });
}

function openModal(itemId) {
  const item = items.find(i => i.id === itemId);
  if (!item) return;

  document.getElementById("modalTitle").innerText = `Vendors for ${item.name}`;
  const tbody = document.getElementById("vendorTableBody");
  tbody.innerHTML = "";

  item.vendors.forEach(vendor => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${vendor.vendor}</td>
      <td>${vendor.sku || "-"}</td>
      <td>${vendor.quantity}</td>
      <td>$${vendor.cost.toFixed(2)}</td>
      <td>${vendor.case_size}</td>
    `;
    tbody.appendChild(row);
  });

  document.getElementById("vendorModal").style.display = "flex";
}

function closeModal() {
  document.getElementById("vendorModal").style.display = "none";
}

function sortByName() {
  sortAsc = !sortAsc;

  const sortedItems = [...items].sort((a, b) => {
    if (a.name < b.name) return sortAsc ? -1 : 1;
    if (a.name > b.name) return sortAsc ? 1 : -1;
    return 0;
  });

  // Optional: update sort arrow indicator
  const th = document.querySelector("th[onclick='sortByName()']");
  th.innerHTML = `Item Name ${sortAsc ? '🔼' : '🔽'}`;

  renderItems(sortedItems);
}

function searchItems() {
  const query = document.getElementById("searchInput").value.toLowerCase();

  const filteredItems = items.filter(item =>
    item.name.toLowerCase().includes(query)
  );

  renderItems(filteredItems);
}

