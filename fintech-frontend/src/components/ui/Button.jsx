import { clsx } from "../../utils/clsx";
import Spinner from "./Spinner";

export default function Button({ children, className, loading, disabled, variant, ...rest }) {
  const baseClasses = "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium disabled:opacity-60 disabled:cursor-not-allowed active:scale-[0.99]";
  
  const variantClasses = variant === "secondary" 
    ? "bg-zinc-200 text-zinc-900 hover:bg-zinc-300 dark:bg-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-600"
    : variant === "outline"
    ? "border border-zinc-300 dark:border-zinc-700 bg-transparent text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
    : "bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200";
  
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      className={clsx(
        baseClasses,
        variantClasses,
        className
      )}
    >
      {loading && <Spinner />} {children}
    </button>
  );
}
