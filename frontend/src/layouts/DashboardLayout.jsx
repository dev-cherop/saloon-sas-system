import { NavLink } from "react-router-dom";

const navigation = [
  { label: "Dashboard", path: "/" },
  { label: "Customers", path: "/customers" },
  { label: "Services", path: "/services" },
  { label: "Appointments", path: "/appointments" },
  { label: "Revenue", path: "/revenue" },
  { label: "Expenses", path: "/expenses" },
  { label: "Workers", path: "/workers" },
  { label: "Reports", path: "/reports" },
];

export default function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="flex h-16 items-center border-b border-slate-200 px-6">
          <div>
            <h1 className="text-lg font-bold text-slate-900">
              Salon Manager
            </h1>
            <p className="text-xs text-slate-500">Management System</p>
          </div>
        </div>

        <nav className="space-y-1 p-4">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                [
                  "block rounded-lg px-4 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                ].join(" ")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 border-t border-slate-200 p-4">
          <NavLink
            to="/settings"
            className="block rounded-lg px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            Settings
          </NavLink>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6">
          <div>
            <p className="text-sm font-medium text-slate-500">
              Business
            </p>
            <p className="font-semibold text-slate-900">
              My Salon
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium text-slate-900">
                Administrator
              </p>
              <p className="text-xs text-slate-500">
                Admin
              </p>
            </div>

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white">
              A
            </div>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}