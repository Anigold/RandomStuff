// src/ui/Modal.jsx
export default function Modal({ children, onClose }) {
    return (
      <div
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <div
          className="bg-zinc-900 max-h-[90vh] w-full max-w-3xl rounded-lg shadow-lg overflow-hidden relative text-white"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={onClose}
            className="absolute top-2 right-3 text-zinc-400 hover:text-white text-lg"
          >
            ✕
          </button>
          <div className="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-3rem)]">
            {children}
          </div>
        </div>
      </div>
    );
  }
  