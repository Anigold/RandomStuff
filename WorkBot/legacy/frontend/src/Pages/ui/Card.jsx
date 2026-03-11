// src/ui/Card.jsx
export default function Card({ children, onClick }) {
    return (
      <div
        onClick={onClick}
        className="bg-zinc-800 p-4 rounded-lg shadow hover:bg-zinc-700 cursor-pointer transition-colors"
      >
        {children}
      </div>
    );
  }
  