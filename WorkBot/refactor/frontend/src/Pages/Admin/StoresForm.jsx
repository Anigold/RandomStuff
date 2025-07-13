// src/admin/StoresForm.jsx
import React, { useState } from 'react';

function StoresForm() {
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('/api/stores', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ store_name: name, address }),
    });
    setName('');
    setAddress('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Add Store</h3>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="Store Name" required />
      <input value={address} onChange={e => setAddress(e.target.value)} placeholder="Address" required />
      <button type="submit">Add Store</button>
    </form>
  );
}

export default StoresForm;
