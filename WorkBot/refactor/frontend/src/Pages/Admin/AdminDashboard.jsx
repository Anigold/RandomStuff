// src/admin/AdminDashboard.jsx
import React from 'react';
import VendorsForm from './VendorsForm';
import ItemsForm from './ItemsForm';
import StoresForm from './StoresForm';

function AdminDashboard() {
  return (
    <div className="scrollable-content">
      <h2>Admin Dashboard</h2>
      <VendorsForm />
      <hr />
      <ItemsForm />
      <hr />
      <StoresForm />
    </div>
  );
}

export default AdminDashboard;
