// src/ui/Button.jsx
export default function Button({ children, onClick, className = "", type = "button" }) {
    return (
      <button
        type={type}
        onClick={onClick}
        className={`px-4 py-2 rounded font-medium transition-colors ${className}`}
      >
        {children}
      </button>
    );
  }
  