// src/ui/PageLayout.jsx
export default function PageLayout({ children }) {
    return (
      <div className="p-6 overflow-y-auto text-zinc-300 space-y-4 h-full">
        {children}
      </div>
    );
  }
  