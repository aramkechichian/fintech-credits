import { clsx } from "../../utils/clsx";

export default function Input({ label, helperText, className, ...props }) {
  if (label || helperText) {
    return (
      <div className="space-y-1">
        {label && (
          <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
            {label}
          </label>
        )}
        <input
          {...props}
          className={clsx(
            "w-full rounded-xl border border-cyan-300 dark:border-cyan-700 bg-white dark:bg-zinc-900 px-3 py-2 text-sm transition-colors",
            "focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 dark:focus:ring-cyan-500 dark:focus:border-cyan-500",
            className
          )}
        />
        {helperText && (
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }

  return (
    <input
      {...props}
      className={clsx(
        "w-full rounded-xl border border-cyan-300 dark:border-cyan-700 bg-white dark:bg-zinc-900 px-3 py-2 text-sm transition-colors",
        "focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 dark:focus:ring-cyan-500 dark:focus:border-cyan-500",
        className
      )}
    />
  );
}
