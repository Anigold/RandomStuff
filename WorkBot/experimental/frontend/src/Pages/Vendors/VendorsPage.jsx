import React, { useEffect, useState } from 'react';
import './VendorsPage.css'

function VendorsPage() {
  const [vendors, setVendors] = useState([]);

  useEffect(() => {
    fetch('/api/vendors')
      .then(res => res.json())
      .then(setVendors);
  }, []);

  return (
    <div className="scrollable-content">
      <h2>Vendors</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Min Order $</th>
            <th>Min Cases</th>
          </tr>
        </thead>
        <tbody>
          {vendors.map(v => (
            <tr key={v.id}>
              <td>{v.name}</td>
              <td>{(v.minimum_order_cost / 100).toFixed(2)}</td>
              <td>{v.minimum_order_cases}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default VendorsPage;
