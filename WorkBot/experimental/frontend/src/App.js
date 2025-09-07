import React, { useState } from 'react';
import ItemsPage from './Pages/Items/Items';
import AdminDashboard from './Pages/Admin/AdminDashboard';
import VendorsPage from './Pages/Vendors/VendorsPage';
import SidebarButton from './Pages/ui/SidebarButton';
import StoresPage from './Pages/Stores/StoresPage';
import OrdersPage from './Pages/Orders/OrdersPage';

function App() {
  const [page, setPage] = useState("home");

  const renderContent = () => {
    if (page === "items")   return <ItemsPage />;
    if (page === "admin")   return <AdminDashboard />;
    if (page === "vendors") return <VendorsPage />;
    if (page === 'stores')  return <StoresPage />;
    if (page === 'orders')  return <OrdersPage />;


    return (
      <div className="overflow-y-auto max-h-full space-y-2">
        <h2 className="text-2xl font-semibold text-white">Welcome to WorkBot</h2>
        <p className="text-zinc-400">
          This is your landing page content. Everything here scrolls, but the header and sidebar remain fixed.
        </p>
        {[...Array(50)].map((_, i) => (
          <p key={i} className="text-zinc-500">Line {i + 1}</p>
        ))}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-900 text-white font-sans">
      {/* Top Bar */}
      <header className="bg-zinc-800 px-6 py-4 border-b border-zinc-700 shadow">
        <h1 className="text-xl font-bold tracking-wide">WorkBot Dashboard</h1>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-60 bg-zinc-800 border-r border-zinc-700 p-4">
            <nav>
            <ul className="space-y-2">
                <SidebarButton label="Home" onClick={() => setPage("home")} />
                <SidebarButton label="Orders" onClick={() => setPage("orders")} />
                <SidebarButton label="Items" onClick={() => setPage("items")} />
                <SidebarButton label="Vendors" onClick={() => setPage("vendors")} />
                <SidebarButton label="Admin" onClick={() => setPage("admin")} />
                <SidebarButton label="Stores" onClick={() => setPage("stores")} />
            </ul>

          </nav>
        </aside>

        {/* Content Area */}
        <main className="flex-1 p-6 overflow-y-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;
