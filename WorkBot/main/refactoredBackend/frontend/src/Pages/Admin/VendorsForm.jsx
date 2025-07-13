// src/admin/VendorsForm.jsx
import React, { useState } from 'react';

function VendorsForm() {
  const [name, setName] = useState('');
  const [minCost, setMinCost] = useState('');
  const [minCases, setMinCases] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch('/api/vendors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, minimum_order_cost: minCost, minimum_order_cases: minCases }),
    });
    setName('');
    setMinCost('');
    setMinCases('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Add Vendor</h3>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="Vendor Name" required />
      <input value={minCost} onChange={e => setMinCost(e.target.value)} placeholder="Min Order Cost" type="number" />
      <input value={minCases} onChange={e => setMinCases(e.target.value)} placeholder="Min Order Cases" type="number" />
      <button type="submit">Add Vendor</button>
    </form>
  );
}

export default VendorsForm;
