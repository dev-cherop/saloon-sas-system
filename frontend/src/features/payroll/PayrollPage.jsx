import { useCallback, useEffect, useMemo, useState } from "react";
import { getPayroll, createPayroll, updatePayroll, updatePayrollStatus } from "../../services/payrollApi";
import { getWorkers } from "../../services/workerApi";

const emptyForm = {
  worker_id: "",
  period_start: "",
  period_end: "",
  base_pay: "",
  commission: "0",
  bonus: "0",
  deductions: "0",
  notes: "",
};

const paymentMethods = [
  ["cash", "Cash"],
  ["mobile_money", "Mobile money"],
  ["card", "Card"],
  ["bank_transfer", "Bank transfer"],
];

const money = (value) =>
  new Intl.NumberFormat("en-UG", {
    style: "currency",
    currency: "UGX",
    maximumFractionDigits: 2,
  }).format(Number(value || 0));

const dateLabel = (value) =>
  value ? new Date(`${value}T00:00:00`).toLocaleDateString() : "—";

export default function PayrollPage({ businessId }) {
  const [records, setRecords] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [statusFilter, setStatusFilter] = useState("all");
  const [paymentRecord, setPaymentRecord] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState("cash");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [payrollResponse, workersResponse] = await Promise.all([
        getPayroll(businessId),
        getWorkers(businessId),
      ]);
      setRecords(payrollResponse.data);
      setWorkers(workersResponse.data);
    } catch {
      setError("Failed to load payroll. Check your access and try again.");
    } finally {
      setLoading(false);
    }
  }, [businessId]);

  useEffect(() => {
    if (businessId) loadData();
  }, [businessId, loadData]);

  const workerNames = useMemo(
    () =>
      Object.fromEntries(
        workers.map((worker) => [
          worker.id,
          `${worker.first_name} ${worker.last_name}`,
        ]),
      ),
    [workers],
  );

  const filteredRecords = records.filter(
    (record) => statusFilter === "all" || record.status === statusFilter,
  );

  const totals = useMemo(
    () =>
      records.reduce(
        (summary, record) => {
          summary[record.status] += Number(record.net_pay || 0);
          return summary;
        },
        { draft: 0, approved: 0, paid: 0 },
      ),
    [records],
  );

  const calculatedNetPay =
    Number(form.base_pay || 0) +
    Number(form.commission || 0) +
    Number(form.bonus || 0) -
    Number(form.deductions || 0);

  function startCreate() {
    setEditingRecord(null);
    setForm(emptyForm);
    setError("");
    setNotice("");
    setShowForm(true);
  }

  function startEdit(record) {
    setEditingRecord(record);
    setForm({
      worker_id: record.worker_id,
      period_start: record.period_start,
      period_end: record.period_end,
      base_pay: String(record.base_pay),
      commission: String(record.commission),
      bonus: String(record.bonus),
      deductions: String(record.deductions),
      notes: record.notes || "",
    });
    setError("");
    setNotice("");
    setShowForm(true);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");

    const payload = {
      period_start: form.period_start,
      period_end: form.period_end,
      base_pay: Number(form.base_pay),
      commission: Number(form.commission || 0),
      bonus: Number(form.bonus || 0),
      deductions: Number(form.deductions || 0),
      notes: form.notes.trim() || null,
    };

    try {
      if (editingRecord) {
        await updatePayroll(businessId, editingRecord.id, payload);
        setNotice("Draft payroll updated.");
      } else {
        await createPayroll(businessId, {
          ...payload,
          worker_id: form.worker_id,
        });
        setNotice("Payroll record created.");
      }
      setShowForm(false);
      setEditingRecord(null);
      setForm(emptyForm);
      await loadData();
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Could not save payroll. Check the entered details and try again.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(record, status, method) {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      await updatePayrollStatus(businessId, record.id, {
        status,
        ...(status === "paid" ? { payment_method: method } : {}),
      });
      setPaymentRecord(null);
      setNotice(status === "paid" ? "Payroll marked as paid." : "Payroll approved.");
      await loadData();
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Could not update payroll status. Please try again.",
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-slate-500">Loading payroll...</p>;
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Worker Payroll</h1>
          <p className="mt-1 text-sm text-slate-500">
            Prepare, approve, and record payments for your salon team.
          </p>
        </div>
        <button
          type="button"
          onClick={showForm ? () => setShowForm(false) : startCreate}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          {showForm ? "Cancel" : "Create Payroll"}
        </button>
      </div>

      {error && (
        <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}
      {notice && (
        <p role="status" className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700">
          {notice}
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          ["Draft total", totals.draft],
          ["Approved total", totals.approved],
          ["Paid total", totals.paid],
        ].map(([label, total]) => (
          <div key={label} className="rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-xl font-semibold text-slate-900">{money(total)}</p>
          </div>
        ))}
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-xl border border-slate-200 bg-white p-6"
        >
          <h2 className="text-lg font-semibold text-slate-900">
            {editingRecord ? "Edit draft payroll" : "New payroll record"}
          </h2>

          {!editingRecord && (
            <div>
              <label htmlFor="payroll-worker" className="mb-1 block text-sm font-medium text-slate-700">
                Worker
              </label>
              <select
                id="payroll-worker"
                required
                value={form.worker_id}
                onChange={(event) => setForm({ ...form, worker_id: event.target.value })}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="">Select worker</option>
                {workers.filter((worker) => worker.is_active).map((worker) => (
                  <option key={worker.id} value={worker.id}>
                    {worker.first_name} {worker.last_name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            {[
              ["period_start", "Period start", "date"],
              ["period_end", "Period end", "date"],
              ["base_pay", "Base pay (UGX)", "number"],
              ["commission", "Commission (UGX)", "number"],
              ["bonus", "Bonus (UGX)", "number"],
              ["deductions", "Deductions (UGX)", "number"],
            ].map(([name, label, type]) => (
              <div key={name}>
                <label htmlFor={`payroll-${name}`} className="mb-1 block text-sm font-medium text-slate-700">
                  {label}
                </label>
                <input
                  id={`payroll-${name}`}
                  type={type}
                  required={["period_start", "period_end", "base_pay"].includes(name)}
                  min={type === "number" ? "0" : undefined}
                  step={type === "number" ? "0.01" : undefined}
                  value={form[name]}
                  onChange={(event) => setForm({ ...form, [name]: event.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                />
              </div>
            ))}
          </div>

          <div className="rounded-lg bg-slate-50 p-4">
            <p className="text-sm text-slate-500">Calculated net pay</p>
            <p className="mt-1 text-xl font-semibold text-slate-900">{money(calculatedNetPay)}</p>
            {calculatedNetPay < 0 && (
              <p className="mt-1 text-sm text-red-600">
                Deductions exceed gross pay. Adjust the amounts before saving.
              </p>
            )}
          </div>

          <div>
            <label htmlFor="payroll-notes" className="mb-1 block text-sm font-medium text-slate-700">
              Notes (optional)
            </label>
            <textarea
              id="payroll-notes"
              rows={3}
              value={form.notes}
              onChange={(event) => setForm({ ...form, notes: event.target.value })}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>

          <button
            type="submit"
            disabled={saving || calculatedNetPay < 0 || !form.period_start || !form.period_end}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {saving ? "Saving..." : editingRecord ? "Update draft" : "Save draft"}
          </button>
        </form>
      )}

      {paymentRecord && (
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="font-semibold text-slate-900">Record payroll payment</h2>
          <p className="mt-1 text-sm text-slate-500">
            {workerNames[paymentRecord.worker_id] || "Worker"} · {money(paymentRecord.net_pay)}
          </p>
          <div className="mt-4 flex flex-wrap items-end gap-3">
            <div>
              <label htmlFor="payroll-payment-method" className="mb-1 block text-sm font-medium text-slate-700">
                Payment method
              </label>
              <select
                id="payroll-payment-method"
                value={paymentMethod}
                onChange={(event) => setPaymentMethod(event.target.value)}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                {paymentMethods.map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <button
              type="button"
              disabled={saving}
              onClick={() => handleStatusChange(paymentRecord, "paid", paymentMethod)}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {saving ? "Processing..." : "Confirm payment"}
            </button>
            <button
              type="button"
              onClick={() => setPaymentRecord(null)}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-900">Payroll records</h2>
        <select
          aria-label="Filter payroll by status"
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
        >
          <option value="all">All statuses</option>
          <option value="draft">Draft</option>
          <option value="approved">Approved</option>
          <option value="paid">Paid</option>
        </select>
      </div>

      {filteredRecords.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center">
          <p className="font-medium text-slate-700">No payroll records found</p>
          <p className="mt-1 text-sm text-slate-500">
            Create a draft payroll record to get started.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-left">
            <thead className="bg-slate-50">
              <tr>
                {["Worker", "Period", "Base pay", "Commission", "Bonus", "Deductions", "Net pay", "Status", "Payment method", "Actions"].map((heading) => (
                  <th key={heading} className="whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase text-slate-500">
                    {heading}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredRecords.map((record) => (
                <tr key={record.id}>
                  <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-slate-900">
                    {workerNames[record.worker_id] || "Unknown worker"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                    {dateLabel(record.period_start)} – {dateLabel(record.period_end)}
                  </td>
                  {[record.base_pay, record.commission, record.bonus, record.deductions, record.net_pay].map((amount, index) => (
                    <td key={index} className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                      {money(amount)}
                    </td>
                  ))}
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                      record.status === "paid"
                        ? "bg-emerald-100 text-emerald-800"
                        : record.status === "approved"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-amber-100 text-amber-800"
                    }`}>
                      {record.status}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                    {paymentMethods.find(([value]) => value === record.payment_method)?.[1] || "—"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm">
                    <div className="flex items-center gap-2">
                      {record.status === "draft" && (
                        <>
                          <button type="button" onClick={() => startEdit(record)} className="font-medium text-slate-700 hover:text-slate-900">
                            Edit
                          </button>
                          <button type="button" disabled={saving} onClick={() => handleStatusChange(record, "approved")} className="font-medium text-blue-700 hover:text-blue-900 disabled:opacity-50">
                            Approve
                          </button>
                        </>
                      )}
                      {record.status === "approved" && (
                        <button
                          type="button"
                          disabled={saving}
                          onClick={() => {
                            setPaymentRecord(record);
                            setPaymentMethod("cash");
                          }}
                          className="font-medium text-emerald-700 hover:text-emerald-900 disabled:opacity-50"
                        >
                          Mark paid
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
