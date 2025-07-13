// src/admin/ItemsForm.jsx
import React, { useState } from 'react';

function ItemsForm() {
  const [name, setName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('/api/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_name: name }),
    });
    setName('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Add Item</h3>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="Item Name" required />
      <button type="submit">Add Item</button>
    </form>
  );
}

export default ItemsForm;
