import { useCallback, useEffect, useState } from "react";

import {
  createCustomerVisit,
  getCustomerVisits,
  getCustomerSpendingSummary,
} from "../../services/customerApi";



export default function CustomerVisitHistory({
  businessId,
  customer,
  onClose,
}) {
  const [visits, setVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(null);
  const [summaryError, setSummaryError] = useState("");
  const [form, setForm] = useState({
    service_name: "",
    amount: "",
    visited_at: new Date().toISOString().slice(0, 16),
    notes: "",
  });


  
const loadVisits = useCallback(async () => {
  setLoading(true);
  setError("");
  setSummaryError("");

  try {
    const [visitData, summaryData] = await Promise.all([
      getCustomerVisits(businessId, customer.id),
      getCustomerSpendingSummary(businessId, customer.id),
    ]);

    setVisits(visitData);
    setSummary(summaryData);
  } catch (err) {
    const message =
      err.response?.data?.detail ||
      "Failed to load customer history and summary.";

    setError(message);
  } finally {
    setLoading(false);
  }
}, [businessId, customer.id]);


  useEffect(() => {
    loadVisits();
  }, [loadVisits]);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!form.service_name.trim() || !form.amount) {
      setError("Enter the service name and amount.");
      return;
    }

    setSaving(true);
    setError("");

    try {
      await createCustomerVisit(
        businessId,
        customer.id,
        {
          service_name: form.service_name.trim(),
          amount: form.amount,
          visited_at: form.visited_at
            ? new Date(form.visited_at).toISOString()
            : null,
          notes: form.notes.trim() || null,
        }
      );

      setForm({
        service_name: "",
        amount: "",
        visited_at: new Date().toISOString().slice(0, 16),
        notes: "",
      });

      await loadVisits();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to record the service."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="space-y-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-slate-900">
            Service History
          </h3>
          <p className="text-sm text-slate-500">
            {customer.first_name} {customer.last_name}
          </p>
        </div>

{summaryError && (
  <p role="alert" className="text-sm text-red-600">
    {summaryError}
  </p>
)}

{summary && (
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      <div className="rounded-lg bg-slate-50 p-4">
        <p className="text-sm text-slate-500">Total Spent</p>
        <p className="mt-1 text-xl font-bold text-slate-900">
          {Number(summary.total_spent).toLocaleString()}
        </p>
      </div>

      <div className="rounded-lg bg-slate-50 p-4">
        <p className="text-sm text-slate-500">Total Visits</p>
        <p className="mt-1 text-xl font-bold text-slate-900">
          {summary.total_visits}
        </p>
      </div>

      <div className="rounded-lg bg-slate-50 p-4">
        <p className="text-sm text-slate-500">Average Spend</p>
        <p className="mt-1 text-xl font-bold text-slate-900">
          {Number(summary.average_spend).toLocaleString()}
        </p>
      </div>

      <div className="rounded-lg bg-slate-50 p-4">
        <p className="text-sm text-slate-500">Last Visit</p>
        <p className="mt-1 text-sm font-bold text-slate-900">
          {summary.last_visit
            ? new Date(summary.last_visit).toLocaleDateString()
            : "No visits yet"}
        </p>
      </div>
    </div>

    <div>
      <h4 className="mb-2 font-semibold text-slate-900">
        Most Frequent Services
      </h4>

      {summary.most_frequent_services.length === 0 ? (
        <p className="text-sm text-slate-500">
          No services recorded yet.
        </p>
      ) : (
        <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200">
          {summary.most_frequent_services.map((service) => (
            <li
              key={service.service_name}
              className="flex items-center justify-between gap-4 p-3"
            >
              <div>
                <p className="font-medium text-slate-800">
                  {service.service_name}
                </p>
                <p className="text-sm text-slate-500">
                  {service.visit_count} visit
                  {service.visit_count === 1 ? "" : "s"}
                </p>
              </div>

              <p className="text-sm font-semibold text-slate-900">
                {Number(service.total_spent).toLocaleString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  </div>
)}
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Close
        </button>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2"
      >
        <div>
          <label
            htmlFor="visit-service"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Service *
          </label>
          <input
            id="visit-service"
            required
            maxLength={150}
            value={form.service_name}
            onChange={(event) =>
              setForm({
                ...form,
                service_name: event.target.value,
              })
            }
            placeholder="e.g. Hair braiding"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
        </div>

        <div>
          <label
            htmlFor="visit-amount"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Amount *
          </label>
          <input
            id="visit-amount"
            type="number"
            required
            min="0.01"
            max="9999999999.99"
            step="0.01"
            value={form.amount}
            onChange={(event) =>
              setForm({
                ...form,
                amount: event.target.value,
              })
            }
            placeholder="e.g. 50000"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
        </div>

        <div>
          <label
            htmlFor="visit-date"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Visit date and time
          </label>
          <input
            id="visit-date"
            type="datetime-local"
            value={form.visited_at}
            onChange={(event) =>
              setForm({
                ...form,
                visited_at: event.target.value,
              })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
        </div>

        <div>
          <label
            htmlFor="visit-notes"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Notes
          </label>
          <input
            id="visit-notes"
            value={form.notes}
            onChange={(event) =>
              setForm({
                ...form,
                notes: event.target.value,
              })
            }
            placeholder="Optional notes"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
        </div>

        <div className="sm:col-span-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving ? "Saving..." : "Record Visit"}
          </button>
        </div>
      </form>

      <div>
        <h4 className="mb-3 font-semibold text-slate-900">
          Previous Visits
        </h4>

        {loading ? (
          <p className="text-sm text-slate-500">
            Loading service history...
          </p>
        ) : visits.length === 0 ? (
          <p className="rounded-lg bg-slate-50 p-4 text-sm text-slate-500">
            No service visits recorded yet.
          </p>
        ) : (
          <div className="divide-y divide-slate-200">
            {visits.map((visit) => (
              <article key={visit.id} className="py-4">
                <div className="flex flex-col justify-between gap-1 sm:flex-row">
                  <p className="font-medium text-slate-900">
                    {visit.service_name}
                  </p>
                  <p className="font-semibold text-slate-900">
                    {Number(visit.amount).toLocaleString(
                      undefined,
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </p>
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  {new Date(visit.visited_at).toLocaleString()}
                </p>

                {visit.notes && (
                  <p className="mt-2 text-sm text-slate-600">
                    {visit.notes}
                  </p>
                )}
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
