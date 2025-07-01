// src/App.js
import React, { useState } from 'react';
import './App.css';
import ItemsPage from './Pages/Items/Items'
import AdminDashboard from './Pages/Admin/AdminDashboard';
import VendorsPage from './Pages/Vendors/VendorsPage';

function App() {
  const [page, setPage] = useState("home"); // ✅ must be declared before use

  const renderContent = () => {
    if (page === "items") {
      return <ItemsPage />;
    }

    if (page === 'admin') {
      return <AdminDashboard />;
    }

    if (page === "vendors") return <VendorsPage />;


    return (
      <div className="scrollable-content">
        <h2>Welcome to WorkBot</h2>
        <p>This is your landing page content. Everything here scrolls, but the header and sidebar remain fixed.</p>
        {[...Array(50)].map((_, i) => <p key={i}>Line {i+1}</p>)}
      </div>
    );
  };

  return (
    <div className="app-container">
      <header className="top-bar">
        <h1>WorkBot Dashboard</h1>
      </header>

      <div className="main-layout">
        <aside className="side-bar">
          <nav>
            <ul>
              <li><button onClick={() => setPage("home")}>Home</button></li>
              <li><button onClick={() => setPage("orders")}>Orders</button></li>
              <li><button onClick={() => setPage("items")}>Items</button></li>
              <li><button onClick={() => setPage("vendors")}>Vendors</button></li>
              <li><button onClick={() => setPage("admin")}>Admin</button></li>
            </ul>
          </nav>
        </aside>

        <main className="content-area">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;
