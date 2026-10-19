import { useCallback, useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getBusinessReport } from "../../services/reportApi";

const STATUS_COLORS = {
  scheduled: "#6366f1",
  confirmed: "#0ea5e9",
  completed: "#10b981",
  cancelled: "#ef4444",
  no_show: "#f59e0b",
};

const PAYMENT_COLORS = [
  "#6366f1",
  "#0ea5e9",
  "#10b981",
  "#f59e0b",
  "#ec4899",
];

function formatMoney(value) {
  return new Intl.NumberFormat("en-UG", {
    style: "currency",
    currency: "UGX",
    maximumFractionDigits: 0,
  }).format(Number(value ?? 0));
}

function getDateString(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getInitialDates() {
  const today = new Date();

  return {
    startDate: getDateString(
      new Date(today.getFullYear(), today.getMonth(), 1)
    ),
    endDate: getDateString(today),
  };
}

function SummaryCard({ label, value, description, valueClass = "" }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`mt-3 break-words text-2xl font-bold ${valueClass}`}>
        {value}
      </p>
      <p className="mt-2 text-xs text-slate-500">{description}</p>
    </div>
  );
}

function ChartCard({ title, description, children }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="font-semibold text-slate-900">{title}</h2>
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      </div>
      {children}
    </section>
  );
}

export default function ReportsPage({ businessId }) {
  const initialDates = getInitialDates();

  const [startDate, setStartDate] = useState(initialDates.startDate);
  const [endDate, setEndDate] = useState(initialDates.endDate);
  const [appliedDates, setAppliedDates] = useState(initialDates);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadReport = useCallback(async () => {
    if (!businessId) {
      setReport(null);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await getBusinessReport(
        businessId,
        appliedDates.startDate,
        appliedDates.endDate
      );
      setReport(data);
    } catch (err) {
      setReport(null);
      setError(
        err.response?.data?.detail ||
          "Unable to load the report. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, [businessId, appliedDates]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  function handleSubmit(event) {
    event.preventDefault();

    if (!startDate || !endDate) {
      setError("Please select both dates.");
      return;
    }

    if (startDate > endDate) {
      setError("The start date must be on or before the end date.");
      return;
    }

    setAppliedDates({ startDate, endDate });
  }

  function resetDates() {
    const dates = getInitialDates();
    setStartDate(dates.startDate);
    setEndDate(dates.endDate);
    setAppliedDates(dates);
    setError("");
  }

  const dailyData = (report?.daily_totals ?? []).map((item) => ({
    ...item,
    revenue: Number(item.revenue ?? 0),
    expenses: Number(item.expenses ?? 0),
    label: item.date,
  }));

  const statusData = Object.entries(
    report?.appointments_by_status ?? {}
  )
    .map(([status, count]) => ({
      name: status.replace("_", " "),
      value: Number(count ?? 0),
      color: STATUS_COLORS[status] ?? "#94a3b8",
    }))
    .filter((item) => item.value > 0);

  const paymentData = (report?.revenue_by_payment_method ?? []).map(
    (item, index) => ({
      name: item.method.replace("_", " "),
      total: Number(item.total ?? 0),
      color: PAYMENT_COLORS[index % PAYMENT_COLORS.length],
    })
  );

  function exportCsv() {
    if (!report) return;

    const rows = [
      ["Salon Management System - Business Report"],
      ["Start date", report.start_date],
      ["End date", report.end_date],
      [],
      ["Metric", "Value"],
      ["Total revenue", report.total_revenue],
      ["Total expenses", report.total_expenses],
      ["Net profit", report.net_profit],
      ["Appointments", report.appointment_count],
      [],
      ["Payment method", "Revenue"],
      ...paymentData.map((item) => [item.name, item.total]),
      [],
      ["Appointment status", "Count"],
      ...Object.entries(report.appointments_by_status ?? {}).map(
        ([status, count]) => [status, count]
      ),
      [],
      ["Date", "Revenue", "Expenses"],
      ...dailyData.map((item) => [
        item.date,
        item.revenue,
        item.expenses,
      ]),
    ];

    const csv = rows
      .map((row) =>
        row
          .map((value) => {
            const text = String(value ?? "");
            return `"${text.replace(/"/g, '""')}"`;
          })
          .join(",")
      )
      .join("\r\n");

    const blob = new Blob(["\uFEFF", csv], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `salon-report-${report.start_date}-to-${report.end_date}.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  if (!businessId) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h1 className="text-xl font-semibold text-slate-900">Reports</h1>
        <p className="mt-2 text-sm text-slate-600">
          Select an active business to view reports.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Reports
          </h1>
          <p className="mt-1 text-sm text-slate-600">
            Monitor revenue, expenses, profit, and appointment performance.
          </p>
        </div>

        <button
          type="button"
          onClick={exportCsv}
          disabled={!report || loading}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Export CSV
        </button>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      >
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 lg:items-end">
          <div>
            <label
              htmlFor="report-start-date"
              className="mb-1.5 block text-sm font-medium text-slate-700"
            >
              Start date
            </label>
            <input
              id="report-start-date"
              type="date"
              value={startDate}
              max={endDate || undefined}
              onChange={(event) => setStartDate(event.target.value)}
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
            />
          </div>

          <div>
            <label
              htmlFor="report-end-date"
              className="mb-1.5 block text-sm font-medium text-slate-700"
            >
              End date
            </label>
            <input
              id="report-end-date"
              type="date"
              value={endDate}
              min={startDate || undefined}
              max={getDateString(new Date())}
              onChange={(event) => setEndDate(event.target.value)}
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60"
          >
            {loading ? "Loading..." : "Generate Report"}
          </button>

          <button
            type="button"
            onClick={resetDates}
            disabled={loading}
            className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
          >
            This Month
          </button>
        </div>
      </form>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      {loading && (
        <p role="status" className="text-sm text-slate-500">
          Loading report data...
        </p>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          label="Total Revenue"
          value={report ? formatMoney(report.total_revenue) : "—"}
          description="Payments received during this period"
        />
        <SummaryCard
          label="Total Expenses"
          value={report ? formatMoney(report.total_expenses) : "—"}
          description="Expenses recorded during this period"
        />
        <SummaryCard
          label="Net Profit"
          value={report ? formatMoney(report.net_profit) : "—"}
          description="Revenue minus expenses"
          valueClass={
            Number(report?.net_profit ?? 0) < 0
              ? "text-red-600"
              : "text-emerald-700"
          }
        />
        <SummaryCard
          label="Appointments"
          value={
            report
              ? Number(report.appointment_count ?? 0).toLocaleString("en-UG")
              : "—"
          }
          description="Appointments scheduled in this period"
        />
      </div>

      {report && !loading && (
        <>
          <ChartCard
            title="Revenue vs. Expenses"
            description="Daily payment revenue compared with recorded expenses."
          >
            {dailyData.length ? (
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={dailyData}
                    margin={{ top: 10, right: 12, left: 12, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis
                      dataKey="label"
                      tick={{ fontSize: 11 }}
                      minTickGap={20}
                    />
                    <YAxis
                      tickFormatter={(value) =>
                        new Intl.NumberFormat("en-UG", {
                          notation: "compact",
                          maximumFractionDigits: 1,
                        }).format(value)
                      }
                      tick={{ fontSize: 11 }}
                      width={65}
                    />
                    <Tooltip
                      formatter={(value, name) => [
                        formatMoney(value),
                        name === "revenue" ? "Revenue" : "Expenses",
                      ]}
                    />
                    <Legend />
                    <Bar
                      dataKey="revenue"
                      name="Revenue"
                      fill="#4f46e5"
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar
                      dataKey="expenses"
                      name="Expenses"
                      fill="#f59e0b"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="py-12 text-center text-sm text-slate-500">
                No revenue or expense records found for this period.
              </p>
            )}
          </ChartCard>

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <ChartCard
              title="Appointments by Status"
              description="Distribution of appointments in the selected period."
            >
              {statusData.length ? (
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={statusData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        label={({ name, value }) => `${name}: ${value}`}
                      >
                        {statusData.map((item) => (
                          <Cell key={item.name} fill={item.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="py-12 text-center text-sm text-slate-500">
                  No appointments found for this period.
                </p>
              )}
            </ChartCard>

            <ChartCard
              title="Revenue by Payment Method"
              description="Total revenue received through each payment method."
            >
              {paymentData.length ? (
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={paymentData}
                        dataKey="total"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        label={({ name }) => name}
                      >
                        {paymentData.map((item) => (
                          <Cell key={item.name} fill={item.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => formatMoney(value)}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="py-12 text-center text-sm text-slate-500">
                  No payments found for this period.
                </p>
              )}
            </ChartCard>
          </div>

          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 p-5">
              <h2 className="font-semibold text-slate-900">
                Daily Breakdown
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                {report.start_date} to {report.end_date}
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-slate-600">
                  <tr>
                    <th className="px-5 py-3 font-medium">Date</th>
                    <th className="px-5 py-3 text-right font-medium">
                      Revenue
                    </th>
                    <th className="px-5 py-3 text-right font-medium">
                      Expenses
                    </th>
                    <th className="px-5 py-3 text-right font-medium">
                      Difference
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {dailyData.map((item) => (
                    <tr key={item.date}>
                      <td className="whitespace-nowrap px-5 py-3 text-slate-700">
                        {item.date}
                      </td>
                      <td className="whitespace-nowrap px-5 py-3 text-right text-slate-700">
                        {formatMoney(item.revenue)}
                      </td>
                      <td className="whitespace-nowrap px-5 py-3 text-right text-slate-700">
                        {formatMoney(item.expenses)}
                      </td>
                      <td
                        className={`whitespace-nowrap px-5 py-3 text-right font-medium ${
                          item.revenue - item.expenses < 0
                            ? "text-red-600"
                            : "text-emerald-700"
                        }`}
                      >
                        {formatMoney(item.revenue - item.expenses)}
                      </td>
                    </tr>
                  ))}

                  {!dailyData.length && (
                    <tr>
                      <td
                        colSpan={4}
                        className="px-5 py-8 text-center text-slate-500"
                      >
                        No daily records found for this period.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
