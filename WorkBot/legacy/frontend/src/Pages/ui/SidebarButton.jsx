// src/ui/SidebarButton.jsx
import Button from './Button';

export default function SidebarButton({ label, onClick }) {
  return (
    <li>
      <Button
        onClick={onClick}
        className="w-full text-left text-zinc-200 hover:bg-zinc-700 px-3 py-2"
      >
        {label}
      </Button>
    </li>
  );
}
