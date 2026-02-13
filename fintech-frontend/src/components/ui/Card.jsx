import { clsx } from "../../utils/clsx";

export default function Card({ children, className }) {
  return (
    <div className={clsx("rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm", className)}>
      {children}
    </div>
  );
}
