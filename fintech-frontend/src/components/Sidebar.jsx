import { useTranslation } from "../i18n/I18nContext";

export default function Sidebar({ currentRoute, onNavigate }) {
  const { t } = useTranslation();

  const menuItems = [
    {
      id: "home",
      label: t("sidebar.home"),
      icon: "🏠",
      route: "home",
    },
    {
      id: "country-rules",
      label: t("sidebar.manageCountryRules"),
      icon: "🌍",
      route: "country-rules",
    },
  ];

  return (
    <aside className="w-64 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 min-h-screen fixed left-0 top-16 h-[calc(100vh-4rem)] overflow-y-auto z-10">
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  if (onNavigate) {
                    onNavigate(item.route);
                  }
                }}
                className={`w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 transition-colors ${
                  currentRoute === item.route
                    ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50 font-medium"
                    : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800"
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
