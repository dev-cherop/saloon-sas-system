import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import DashboardLayout from "./layouts/DashboardLayout";
import CustomerPage from "./features/customers/CustomerPage";
import LoginPage from "./features/auth/login";
import LoyaltySettingsPage from "./features/loyalty/LoyalSettingsPage";
import ExpensePage from "./features/expenses/ExpensePage";
import PaymentsPage from "./payments/PaymentsPage";
import ServicesPage from "./features/services/ServicesPage";
import WorkersPage from "./features/workers/WorkersPage";
import AppointmentsPage from "./features/appointments/AppointmentsPage";

import {
  AuthProvider,
  useAuth,
} from "./features/auth/authContext";

import ProtectedRoute from "./routes/ProtectedRoutes";
import PermissionRoute from "./routes/PermissionRoute";

import { useEffect, useState } from "react";
import { getAppointments } from "./services/appointmentApi";
import { getPaymentSummary } from "./services/paymentApi";
import { getPayments } from "./services/paymentApi";
import { getCustomers } from "./services/customerApi";
import { getWorkers } from "./services/workerApi";
import { getServices } from "./services/serviceApi";
import { getBusinessReport } from "./services/reportApi";
import ReportsPage from "./features/reports/ReportsPage";


// Dashboard page
function DashboardPage() {
  const { activeBusiness } = useAuth();

  const [appointments, setAppointments] = useState([]);
  const [revenue, setRevenue] = useState(null);
  const [monthlyReport, setMonthlyReport] = useState(null);
  const [recentPayments, setRecentPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [customerCount, setCustomerCount] = useState(0);
  const [workerCount, setWorkerCount] = useState(0);
  const [customers, setCustomers] = useState([]);
  const [services, setServices] = useState([]);
  const [workers, setWorkers] = useState([]);
  

  useEffect(() => {
    if (!activeBusiness?.id) {
      setAppointments([]);
      setRevenue(null);
      setLoading(false);
      return;
    }

    let cancelled = false;


async function loadDashboard() {
  setLoading(true);
  setError("");

  const today = new Date();

  const monthStart = new Date(
  today.getFullYear(),
  today.getMonth(),
  1
);

const startDate = [
  monthStart.getFullYear(),
  String(monthStart.getMonth() + 1).padStart(2, "0"),
  String(monthStart.getDate()).padStart(2, "0"),
].join("-");

const endDate = [
  today.getFullYear(),
  String(today.getMonth() + 1).padStart(2, "0"),
  String(today.getDate()).padStart(2, "0"),
].join("-");

  const date = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");

  try {
    const results = await Promise.all([
  getAppointments(activeBusiness.id),
  getPaymentSummary(activeBusiness.id, {
    start_date: date,
    end_date: date,
  }),
  getBusinessReport(activeBusiness.id, startDate, endDate),
  getPayments(activeBusiness.id),
  getCustomers(activeBusiness.id),
  getWorkers(activeBusiness.id),
  getServices(activeBusiness.id),
]);

if (!cancelled) {
  setAppointments(results[0].data);
setRevenue(results[1].data);
setMonthlyReport(results[2]);
setRecentPayments(results[3].data.slice(0, 5));

setCustomerCount(results[4].length);
setWorkerCount(results[5].data.length);
setCustomers(results[4]);
setWorkers(results[5].data);
setServices(results[6]);
}
  } catch {
    if (!cancelled) {
      setError("Unable to load dashboard data. Please try again.");
    }
  } finally {
    if (!cancelled) {
      setLoading(false);
    }
  }
}

loadDashboard();

return () => {
  cancelled = true;
};

  }, [activeBusiness?.id]);

  const todayString = new Date().toDateString();

  const todaysAppointments = appointments.filter(
    (appointment) =>
      new Date(appointment.start_time).toDateString() === todayString
  );

  const upcomingAppointments = appointments
  .filter(
    (appointment) =>
      new Date(appointment.start_time) >= new Date() &&
      ["scheduled", "confirmed"].includes(appointment.status)
  )
  .sort(
    (a, b) =>
      new Date(a.start_time) - new Date(b.start_time)
  )
  .slice(0, 5);

const customerById = Object.fromEntries(
  customers.map((customer) => [customer.id, customer])
);

const serviceById = Object.fromEntries(
  services.map((service) => [service.id, service])
);

const workerById = Object.fromEntries(
  workers.map((worker) => [worker.id, worker])
);

const personName = (person) =>
  [person?.first_name, person?.last_name]
    .filter(Boolean)
    .join(" ") || "Unknown";

  const formatMoney = (amount) =>
    new Intl.NumberFormat("en-UG", {
      style: "currency",
      currency: "UGX",
      maximumFractionDigits: 0,
    }).format(Number(amount ?? 0));

  const cards = [
    {
      label: "Today's Appointments",
      value: todaysAppointments.length,
      detail: "Appointments scheduled for today",
    },
    {
      label: "Today's Revenue",
      value: formatMoney(revenue?.total_amount),
      detail: `${revenue?.total_count ?? 0} payments recorded today`,
    },
    {
  label: "Monthly Revenue",
  value: formatMoney(monthlyReport?.total_revenue),
  detail: "Revenue recorded this month",
},
{
  label: "Monthly Expenses",
  value: formatMoney(monthlyReport?.total_expenses),
  detail: "Expenses recorded this month",
},
{
  label: "Monthly Net Profit",
  value: formatMoney(monthlyReport?.net_profit),
  detail: "Revenue minus expenses this month",
},
    {
  label: "Total Customers",
  value: customerCount,
  detail: "Registered customers",
},
{
  label: "Total Workers",
  value: workerCount,
  detail: "Workers registered in the system",
},
  ];

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        Select a business to view its dashboard.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">
          Dashboard
        </h2>
        <p className="mt-2 text-slate-500">
          Welcome to your salon management dashboard.
        </p>
      </div>

      {error && (
        <p className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error}
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <p className="text-sm font-medium text-slate-500">
              {card.label}
            </p>
            <p className="mt-3 text-2xl font-bold text-slate-900">
              {loading ? "Loading..." : card.value}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              {card.detail}
            </p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-lg font-semibold text-slate-900">
          Today's Appointment Overview
        </h3>

        {loading ? (
          <p className="mt-3 text-sm text-slate-500">
            Loading appointments...
          </p>
        ) : (
          <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {["scheduled", "confirmed", "completed", "cancelled"].map(
              (status) => (
                <div key={status} className="rounded-lg bg-slate-50 p-3">
                  <p className="text-sm capitalize text-slate-500">
                    {status}
                  </p>
                  <p className="mt-1 text-xl font-semibold text-slate-900">
                    {
                      todaysAppointments.filter(
                        (appointment) => appointment.status === status
                      ).length
                    }
                  </p>
                </div>
              )
            )}
          </div>
        )}
      </div>
      <div className="rounded-xl border border-slate-200 bg-white p-5">
  <h3 className="text-lg font-semibold text-slate-900">
    Upcoming Appointments
  </h3>

  {loading ? (
    <p className="mt-4 text-sm text-slate-500">
      Loading appointments...
    </p>
  ) : upcomingAppointments.length === 0 ? (
    <p className="mt-4 text-sm text-slate-500">
      No upcoming appointments scheduled.
    </p>
  ) : (
    <div className="mt-4 divide-y divide-slate-100">
      {upcomingAppointments.map((appointment) => (
        <div
          key={appointment.id}
          className="grid gap-2 py-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          <div>
            <p className="font-medium text-slate-900">
              {personName(customerById[appointment.customer_id])}
            </p>
            <p className="text-sm text-slate-500">Customer</p>
          </div>

          <div>
            <p className="font-medium text-slate-900">
              {serviceById[appointment.service_id]?.name || "Unknown service"}
            </p>
            <p className="text-sm text-slate-500">
              Worker: {personName(workerById[appointment.worker_id])}
            </p>
          </div>

          <div>
            <p className="font-medium text-slate-900">
              {new Date(appointment.start_time).toLocaleString(undefined, {
                dateStyle: "medium",
                timeStyle: "short",
              })}
            </p>
            <p className="text-sm text-slate-500">Appointment time</p>
          </div>

          <div>
            <span className="inline-block rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium capitalize text-indigo-700">
              {appointment.status.replace("_", " ")}
            </span>
          </div>
        </div>
      ))}
    </div>
  )}
</div>


      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-lg font-semibold text-slate-900">
          Recent Payments
        </h3>

        {loading ? (
          <p className="mt-4 text-sm text-slate-500">
            Loading payments...
          </p>
        ) : recentPayments.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">
            No recent payments found.
          </p>
        ) : (
          <div className="mt-4 divide-y divide-slate-100">
            {recentPayments.map((payment) => (
              <div
                key={payment.id}
                className="flex flex-col justify-between gap-2 py-4 sm:flex-row sm:items-center"
              >
                <div>
                  <p className="font-medium text-slate-900">
                    {(payment.payment_method || "Unknown method")
                      .replace("_", " ")
                      .replace(/\b\w/g, (letter) => letter.toUpperCase())}
                  </p>
                  <p className="text-sm text-slate-500">
                    {payment.reference || "No reference"}
                  </p>
                </div>

                <div className="sm:text-right">
                  <p className="font-semibold text-slate-900">
                    {formatMoney(payment.amount)}
                  </p>
                  <p className="text-sm text-slate-500">
                    {payment.paid_at
                      ? new Date(payment.paid_at).toLocaleString(undefined, {
                          dateStyle: "medium",
                          timeStyle: "short",
                        })
                      : "Date unavailable"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>



      <div className="rounded-xl border border-slate-200 bg-white p-5">
        <h3 className="text-lg font-semibold text-slate-900">
          Recent Payments
        </h3>

        {loading ? (
          <p className="mt-4 text-sm text-slate-500">
            Loading payments...
          </p>
        ) : recentPayments.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">
            No recent payments found.
          </p>
        ) : (
          <div className="mt-4 divide-y divide-slate-100">
            {recentPayments.slice(0, 5).map((payment) => (
              <div
                key={payment.id}
                className="flex flex-col justify-between gap-2 py-4 sm:flex-row sm:items-center"
              >
                <div>
                  <p className="font-medium text-slate-900">
                    {personName(customerById[payment.customer_id])}
                  </p>
                  <p className="text-sm capitalize text-slate-500">
                    {(payment.method || "Unknown method").replace("_", " ")}
                    {payment.reference ? ` · ${payment.reference}` : ""}
                  </p>
                </div>

                <div className="sm:text-right">
                  <p className="font-semibold text-slate-900">
                    {Number(payment.amount || 0).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                  <p className="text-sm text-slate-500">
                    {payment.paid_at
                      ? new Date(payment.paid_at).toLocaleString(undefined, {
                          dateStyle: "medium",
                          timeStyle: "short",
                        })
                      : "Date unavailable"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>


    </div>

  );
}

// Customers route
function CustomersRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        Your account has no active business membership.
        Contact your administrator.
      </p>
    );
  }

  return (
    <CustomerPage
      businessId={activeBusiness.id}
    />
  );
}

function LoyaltySettingsRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return <p className="text-slate-600">No active business selected.</p>;
  }

  return (
    <LoyaltySettingsPage
      businessId={activeBusiness.id}
      permissions={activeBusiness.permissions ?? []}
    />
  );
}

function ExpensesRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        No active business selected.
      </p>
    );
  }

  return (
    <ExpensePage
      businessId={activeBusiness.id}
      permissions={activeBusiness.permissions ?? []}
    />
  );
}

 function PaymentsRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        No active business selected.
      </p>
    );
  }

  return (
    <PaymentsPage businessId={activeBusiness.id} />
  );
}

function ServicesRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        No active business selected.
      </p>
    );
  }

  return <ServicesPage businessId={activeBusiness.id} />;
}

function WorkersRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        No active business selected.
      </p>
    );
  }

  return <WorkersPage businessId={activeBusiness.id} />;
}


function AppointmentsRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        No active business selected.
      </p>
    );
  }

  return (
    <AppointmentsPage businessId={activeBusiness.id} />
  );
}

function ReportsRoute() {
  const { activeBusiness } = useAuth();

  if (!activeBusiness) {
    return (
      <p className="text-slate-600">
        No active business selected.
      </p>
    );
  }

  return <ReportsPage businessId={activeBusiness.id} />;
}

// Dashboard layout and application routes
function AppLayout() {
  return (
    <DashboardLayout>
      <Routes>
        <Route
          path="/"
          element={<DashboardPage />}
        />

        <Route
          element={
            <PermissionRoute permission="customers:read" />
          }
        >
          <Route
            path="/customers"
            element={<CustomersRoute />}
          />
        </Route>

        <Route element={<PermissionRoute permission="loyalty:read" />}>
  <Route
    path="/loyalty-settings"
    element={<LoyaltySettingsRoute />}
  />
</Route>

<Route element={<PermissionRoute permission="expenses:read" />}>
  <Route
    path="/expenses"
    element={<ExpensesRoute />}
  />
</Route>

<Route element={<PermissionRoute permission="payments:read" />}>
  <Route
    path="/payments"
    element={<PaymentsRoute />}
  />
</Route>

<Route element={<PermissionRoute permission="services:read" />}>
  <Route
    path="/services"
    element={<ServicesRoute />}
  />
</Route>

<Route element={<PermissionRoute permission="workers:read" />}>
  <Route
    path="/workers"
    element={<WorkersRoute />}
  />
</Route>

<Route element={<PermissionRoute permission="appointments:read" />}>
  <Route
    path="/appointments"
    element={<AppointmentsRoute />}
  />
</Route>


          <Route element={<PermissionRoute permission="reports:read" />}>
  <Route
    path="/reports"
    element={<ReportsRoute />}
  />
</Route>

      </Routes>
    </DashboardLayout>
  );
}

// Main application
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public route */}
          <Route
            path="/login"
            element={<LoginPage />}
          />

          {/* Protected application routes */}
          <Route element={<ProtectedRoute />}>
            <Route
              path="/*"
              element={<AppLayout />}
            />
          </Route>

        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}