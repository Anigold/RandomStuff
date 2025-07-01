// src/ItemsPage.jsx
import React, { useEffect, useState } from 'react';
import './Items.css';

function ItemsPage() {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [itemDetails, setItemDetails] = useState(null);

  useEffect(() => {
    fetch("/api/items")
      .then(res => res.json())
      .then(setItems);
  }, []);

  const handleCardClick = (item) => {
    setSelectedItem(item);
    setItemDetails(null); // reset old data

    fetch(`/api/items/${item.id}/details`)
      .then(res => res.json())
      .then(setItemDetails);
  };

  const closeModal = () => {
    setSelectedItem(null);
    setItemDetails(null);
  };

  return (
    <div className="scrollable-content">
      <h2>Item List</h2>
      <div className="item-grid">
        {items.map(item => (
          <div className="item-card" key={item.id} onClick={() => handleCardClick(item)}>
            <h4>{item.item_name}</h4>
          </div>
        ))}
      </div>

      {selectedItem && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Edit Item</h3>

            {!itemDetails ? (
              <p><em>Loading details...</em></p>
            ) : (
              <>
                {/* Editable field */}
                <label>
                  Name:
                  <input
                    type="text"
                    value={itemDetails.item_name}
                    onChange={e =>
                      setItemDetails({ ...itemDetails, item_name: e.target.value })
                    }
                  />
                </label>

                <hr />

                <h4>Vendors</h4>
                <ul>
                  {itemDetails.vendors.map((vendor, i) => (
                    <li key={i}>
                      {vendor.vendor_name} – SKU: {vendor.vendor_sku || 'N/A'} – Price: ${(vendor.price / 100).toFixed(2)}
                    </li>
                  ))}
                </ul>

                <hr />

                <h4>Purchase History</h4>
                <table>
                  <thead>
                    <tr><th>Date</th><th>Store</th><th>Qty</th><th>Unit Cost</th></tr>
                  </thead>
                  <tbody>
                    {itemDetails.purchase_history.map((row, i) => (
                      <tr key={i}>
                        <td>{row.date}</td>
                        <td>{row.store}</td>
                        <td>{row.quantity}</td>
                        <td>${(row.cost_per / 100).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <div style={{ marginTop: '1rem' }}>
                  <button onClick={closeModal}>Cancel</button>
                  <button
                    onClick={async () => {
                      await fetch(`/api/items/${selectedItem.id}`, {
                        method: "PATCH",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ item_name: itemDetails.item_name }),
                      });
                      closeModal();
                      window.location.reload();
                    }}
                    style={{ marginLeft: '1rem' }}
                  >
                    Save Changes
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}


    </div>
  );
}

export default ItemsPage;
