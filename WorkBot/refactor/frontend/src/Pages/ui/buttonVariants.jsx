import { cva } from "class-variance-authority";

export const buttonStyles = cva("rounded px-4 py-2 font-medium transition-colors", {
  variants: {
    intent: {
      primary: "bg-blue-600 text-white hover:bg-blue-700",
      secondary: "bg-zinc-700 text-white hover:bg-zinc-600",
      ghost: "bg-transparent text-zinc-400 hover:bg-zinc-700",
    },
    size: {
      sm: "text-sm",
      md: "text-base",
      lg: "text-lg",
    },
    full: {
      true: "w-full",
      false: ""
    }
  },
  defaultVariants: {
    intent: "primary",
    size: "md",
    full: false
  }
});
