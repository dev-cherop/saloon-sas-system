
import { useEffect, useState } from "react";
import {
  createExpense,
  deleteExpense,
  getExpenses,
  getExpenseSummary,
} from "../../services/expensesApi";

const emptyForm = {
  category: "",
  amount: "",
  expense_date: new Date().toISOString().slice(0, 10),
  description: "",
  payment_method: "cash",
};

const money = (value) =>
  new Intl.NumberFormat("en-UG", {
    style: "currency",
    currency: "UGX",
    maximumFractionDigits: 2,
  }).format(Number(value || 0));

export default function ExpensePage({ businessId, permissions = [] }) {
  const canCreate = permissions.includes("expenses:create");
  const canDelete = permissions.includes("expenses:delete");

  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState({
    total_amount: 0,
    expense_count: 0,
    categories: [],
  });
  const [form, setForm] = useState(emptyForm);
  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    category: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadExpenses() {
    setLoading(true);
    setError("");

    try {
      const activeFilters = Object.fromEntries(
        Object.entries(filters).filter(([, value]) => value !== "")
      );

      const [expenseData, summaryData] = await Promise.all([
        getExpenses(businessId, activeFilters),
        getExpenseSummary(businessId, {
          start_date: filters.start_date || undefined,
          end_date: filters.end_date || undefined,
        }),
      ]);

      setExpenses(expenseData);
      setSummary(summaryData);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load expenses.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadExpenses();
  }, [businessId, filters.start_date, filters.end_date, filters.category]);

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      await createExpense(businessId, {
        ...form,
        amount: form.amount,
        description: form.description || null,
      });

      setForm(emptyForm);
      setSuccess("Expense recorded successfully.");
      await loadExpenses();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save the expense.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(expenseId) {
    if (!window.confirm("Delete this expense permanently?")) return;

    setError("");
    setSuccess("");

    try {
      await deleteExpense(businessId, expenseId);
      setSuccess("Expense deleted.");
      await loadExpenses();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete the expense.");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Expenses</h1>
        <p className="mt-1 text-sm text-slate-500">
          Track salon spending and review expense summaries.
        </p>
      </div>

      {error && (
        <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}
      {success && (
        <p className="rounded-lg bg-green-50 p-3 text-sm text-green-700">
          {success}
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Total expenses</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {money(summary.total_amount)}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Number of expenses</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {summary.expense_count}
          </p>
        </div>
      </div>

      {canCreate && (
        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-xl border border-slate-200 bg-white p-5"
        >
          <h2 className="text-lg font-semibold text-slate-900">
            Record an expense
          </h2>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <label className="text-sm font-medium text-slate-700">
              Category
              <input
                required
                minLength={2}
                maxLength={100}
                value={form.category}
                onChange={(e) =>
                  setForm({ ...form, category: e.target.value })
                }
                placeholder="e.g. Supplies, Rent"
                className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
              />
            </label>

            <label className="text-sm font-medium text-slate-700">
              Amount (UGX)
              <input
                required
                type="number"
                min="0.01"
                step="0.01"
                value={form.amount}
                onChange={(e) =>
                  setForm({ ...form, amount: e.target.value })
                }
                className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
              />
            </label>

            <label className="text-sm font-medium text-slate-700">
              Expense date
              <input
                required
                type="date"
                value={form.expense_date}
                onChange={(e) =>
                  setForm({ ...form, expense_date: e.target.value })
                }
                className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
              />
            </label>

            <label className="text-sm font-medium text-slate-700">
              Payment method
              <select
                value={form.payment_method}
                onChange={(e) =>
                  setForm({ ...form, payment_method: e.target.value })
                }
                className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
              >
                <option value="cash">Cash</option>
                <option value="mobile_money">Mobile money</option>
                <option value="card">Card</option>
                <option value="bank_transfer">Bank transfer</option>
              </select>
            </label>

            <label className="text-sm font-medium text-slate-700 sm:col-span-2">
              Description (optional)
              <input
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                placeholder="What was the expense for?"
                className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Record expense"}
          </button>
        </form>
      )}

      <section className="space-y-4 rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">
          Expense history
        </h2>

        <div className="grid gap-3 sm:grid-cols-3">
          <label className="text-sm text-slate-600">
            From
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) =>
                setFilters({ ...filters, start_date: e.target.value })
              }
              className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
            />
          </label>

          <label className="text-sm text-slate-600">
            To
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) =>
                setFilters({ ...filters, end_date: e.target.value })
              }
              className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
            />
          </label>

          <label className="text-sm text-slate-600">
            Category contains
            <input
              value={filters.category}
              onChange={(e) =>
                setFilters({ ...filters, category: e.target.value })
              }
              placeholder="Search category"
              className="mt-1 w-full rounded-lg border border-slate-300 p-2.5"
            />
          </label>
        </div>

        {loading ? (
          <p className="py-6 text-sm text-slate-500">Loading expenses...</p>
        ) : expenses.length === 0 ? (
          <p className="py-6 text-sm text-slate-500">
            No expenses found for these filters.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-slate-500">
                <tr>
                  <th className="px-3 py-3">Date</th>
                  <th className="px-3 py-3">Category</th>
                  <th className="px-3 py-3">Description</th>
                  <th className="px-3 py-3">Payment</th>
                  <th className="px-3 py-3 text-right">Amount</th>
                  {canDelete && <th className="px-3 py-3">Action</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {expenses.map((expense) => (
                  <tr key={expense.id}>
                    <td className="whitespace-nowrap px-3 py-3">
                      {expense.expense_date}
                    </td>
                    <td className="px-3 py-3 font-medium text-slate-800">
                      {expense.category}
                    </td>
                    <td className="px-3 py-3 text-slate-500">
                      {expense.description || "—"}
                    </td>
                    <td className="px-3 py-3">
                      {expense.payment_method.replace("_", " ")}
                    </td>
                    <td className="whitespace-nowrap px-3 py-3 text-right font-medium">
                      {money(expense.amount)}
                    </td>
                    {canDelete && (
                      <td className="px-3 py-3">
                        <button
                          type="button"
                          onClick={() => handleDelete(expense.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Delete
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">
          Spending by category
        </h2>
        {summary.categories.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">No category totals yet.</p>
        ) : (
          <div className="mt-3 divide-y divide-slate-100">
            {summary.categories.map((item) => (
              <div
                key={item.category}
                className="flex items-center justify-between gap-4 py-3"
              >
                <div>
                  <p className="font-medium text-slate-800">{item.category}</p>
                  <p className="text-xs text-slate-500">
                    {item.expense_count} expense(s)
                  </p>
                </div>
                <p className="font-semibold text-slate-900">
                  {money(item.total_amount)}
                </p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
