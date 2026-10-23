
import { NavLink } from "react-router-dom";
import { useAuth } from "../features/auth/authContext";
import BusinessSwitcher from "../features/auth/BusinessSwitcher";

const navigation = [
  { label: "Dashboard", path: "/", permission: null },
  {
    label: "Customers",
    path: "/customers",
    permission: "customers:read",
  },

  {
  label: "Loyalty Settings",
  path: "/loyalty-settings",
  permission: "loyalty:read",
},
  {
  label: "Expenses",
  path: "/expenses",
  permission: "expenses:read",
},

  {
    label: "Payments",
    path: "/payments",
    permission: "payments:read",
  },
  {
    label: "Checkout",
    path: "/checkout",
    permission: "checkout:read",
  },

  {
    label: "Services",
    path: "/services",
    permission: "services:read",
  },
  {
    label: "Workers",
    path: "/workers",
    permission: "workers:read",
  },

    {
    label: "Appointments",
    path: "/appointments",
    permission: "appointments:read",
  },
  
  {
    label: "Coupons",
    path: "/coupons",
    permission: "coupons:read",
  },

  {
    label: "Reports",
    path: "/reports",
    permission: "reports:read",
  },
];

export default function DashboardLayout({ children }) {
  const { user, logout, activeBusiness } = useAuth();

  const permissions = activeBusiness?.permissions ?? [];

  const visibleNavigation = navigation.filter(
    (item) =>
      item.permission === null ||
      permissions.includes(item.permission),
  );

  const linkClass = ({ isActive }) =>
    [
      "block rounded-lg px-4 py-2.5 text-sm font-medium transition",
      isActive
        ? "bg-slate-900 text-white"
        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
    ].join(" ");

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="flex h-16 items-center border-b border-slate-200 px-6">
          <div>
            <h1 className="text-lg font-bold text-slate-900">
              Salon Manager
            </h1>
            <p className="text-xs text-slate-500">
              Management System
            </p>
          </div>
        </div>

        <nav className="space-y-1 p-4">
          {visibleNavigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={linkClass}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        {permissions.includes("settings:manage") && (
          <div className="absolute bottom-0 left-0 right-0 border-t border-slate-200 p-4">
            <NavLink
              to="/settings"
              className={linkClass}
            >
              Settings
            </NavLink>
          </div>
        )}
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 flex min-h-16 items-center justify-between gap-4 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur sm:px-6">
          <BusinessSwitcher />

          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium text-slate-900">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-slate-500">
                {user?.email}
              </p>
            </div>

            <button
              type="button"
              onClick={logout}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              Logout
            </button>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}