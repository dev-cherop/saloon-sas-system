
import { useCallback, useEffect, useState } from "react";
import { createPayment, getPayments, getPaymentSummary } from "../services/paymentApi";

const initialForm = {
  visit_id: "",
  amount: "",
  payment_method: "cash",
  reference: "",
  notes: "",
};

const money = (value) =>
  Number(value || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

export default function PaymentsPage({ businessId }) {
  const [payments, setPayments] = useState([]);
  const [summary, setSummary] = useState({
    total_amount: 0,
    total_count: 0,
    by_method: [],
  });
  const [form, setForm] = useState(initialForm);
  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadPayments = useCallback(async () => {
    if (!businessId) {
      setPayments([]);
      setSummary({
        total_amount: 0,
        total_count: 0,
        by_method: [],
      });
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    const params = Object.fromEntries(
      Object.entries(filters).filter(([, value]) => value)
    );

    try {
      const [paymentsResponse, summaryResponse] = await Promise.all([
        getPayments(businessId, params),
        getPaymentSummary(businessId, params),
      ]);

      setPayments(paymentsResponse.data);
      setSummary(summaryResponse.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load payments."
      );
    } finally {
      setLoading(false);
    }
  }, [businessId, filters]);

  useEffect(() => {
    loadPayments();
  }, [loadPayments]);

  const handleChange = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleFilterChange = (event) => {
    setFilters((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!businessId) {
      setError("Select a business before recording a payment.");
      return;
    }

    setSaving(true);

    try {
      await createPayment(businessId, {
        visit_id: form.visit_id.trim(),
        amount: form.amount,
        payment_method: form.payment_method,
        reference: form.reference.trim() || null,
        notes: form.notes.trim() || null,
      });

      setForm(initialForm);
      setSuccess("Payment recorded successfully.");
      await loadPayments();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to record payment."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
        <p className="mt-1 text-sm text-gray-500">
          Record payments and track revenue for the selected business.
        </p>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {Array.isArray(error)
            ? error.map((item) => item.msg).join(", ")
            : error}
        </div>
      )}

      {success && (
        <div
          role="status"
          className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700"
        >
          {success}
        </div>
      )}

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Total collected</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">
            {money(summary.total_amount)}
          </p>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Number of payments</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">
            {summary.total_count ?? 0}
          </p>
        </div>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Record payment
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label
                htmlFor="visit_id"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Visit ID
              </label>
              <input
                id="visit_id"
                name="visit_id"
                value={form.visit_id}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                placeholder="Enter customer visit UUID"
              />
            </div>

            <div>
              <label
                htmlFor="amount"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Amount
              </label>
              <input
                id="amount"
                name="amount"
                type="number"
                min="0.01"
                step="0.01"
                value={form.amount}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                placeholder="0.00"
              />
            </div>

            <div>
              <label
                htmlFor="payment_method"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Payment method
              </label>
              <select
                id="payment_method"
                name="payment_method"
                value={form.payment_method}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              >
                <option value="cash">Cash</option>
                <option value="mobile_money">Mobile money</option>
                <option value="card">Card</option>
              </select>
            </div>

            <div>
              <label
                htmlFor="reference"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Reference (optional)
              </label>
              <input
                id="reference"
                name="reference"
                value={form.reference}
                onChange={handleChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
                placeholder="Receipt or transaction reference"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="notes"
              className="mb-1 block text-sm font-medium text-gray-700"
            >
              Notes (optional)
            </label>
            <textarea
              id="notes"
              name="notes"
              value={form.notes}
              onChange={handleChange}
              rows={2}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
              placeholder="Additional payment details"
            />
          </div>

          <button
            type="submit"
            disabled={saving || !businessId}
            
            className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        
            
          >
            {saving ? "Recording..." : "Record payment"}
          </button>
        </form>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <h2 className="text-lg font-semibold text-gray-900">
            Payment history
          </h2>

          <form
            onSubmit={(event) => {
              event.preventDefault();
              loadPayments();
            }}
            className="flex flex-wrap items-end gap-2"
          >
            <div>
              <label
                htmlFor="start_date"
                className="mb-1 block text-xs text-gray-500"
              >
                From
              </label>
              <input
                id="start_date"
                name="start_date"
                type="date"
                value={filters.start_date}
                onChange={handleFilterChange}
                className="rounded-lg border border-gray-300 px-2 py-2 text-sm"
              />
            </div>

            <div>
              <label
                htmlFor="end_date"
                className="mb-1 block text-xs text-gray-500"
              >
                To
              </label>
              <input
                id="end_date"
                name="end_date"
                type="date"
                value={filters.end_date}
                onChange={handleFilterChange}
                className="rounded-lg border border-gray-300 px-2 py-2 text-sm"
              />
            </div>

            <button
              type="submit"
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Apply filters
            </button>
          </form>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                {["Date", "Visit ID", "Method", "Reference", "Amount"].map(
                  (heading) => (
                    <th
                      key={heading}
                      className="px-4 py-3 text-left font-semibold text-gray-600"
                    >
                      {heading}
                    </th>
                  )
                )}
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Loading payments...
                  </td>
                </tr>
              ) : payments.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    No payments found.
                  </td>
                </tr>
              ) : (
                payments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap px-4 py-3">
                      {payment.paid_at
                        ? new Date(payment.paid_at).toLocaleString()
                        : "—"}
                    </td>
                    <td className="max-w-48 truncate px-4 py-3">
                      {payment.visit_id}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 capitalize">
                      {payment.payment_method.replace("_", " ")}
                    </td>
                    <td className="px-4 py-3">
                      {payment.reference || "—"}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 font-medium">
                      {money(payment.amount)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-lg font-semibold text-gray-900">
          Totals by payment method
        </h2>

        {summary.by_method?.length ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {summary.by_method.map((item) => (
              <div
                key={item.payment_method}
                className="rounded-lg bg-gray-50 p-4"
              >
                <p className="text-sm capitalize text-gray-500">
                  {item.payment_method.replace("_", " ")}
                </p>
                <p className="mt-1 text-lg font-semibold text-gray-900">
                  {money(item.total_amount)}
                </p>
                <p className="text-xs text-gray-500">
                  {item.count} payment(s)
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            No payment summary available for this period.
          </p>
        )}
      </section>
    </div>
  );
}
