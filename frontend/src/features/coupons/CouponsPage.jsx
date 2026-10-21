import { useCallback, useEffect, useState } from "react";
import {
  getCoupons,
  createCoupon,
  updateCoupon,
  deleteCoupon,
} from "../../services/couponApi";

const emptyForm = {
  code: "",
  description: "",
  discount_type: "percentage",
  discount_value: "",
  minimum_spend: "0.00",
  usage_limit: "",
  starts_at: "",
  expires_at: "",
  is_active: true,
};

function toDateTimeLocal(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const local = new Date(
    date.getTime() - date.getTimezoneOffset() * 60000
  );
  return local.toISOString().slice(0, 16);
}

function preparePayload(form) {
  return {
    ...form,
    code: form.code.trim().toUpperCase(),
    description: form.description.trim() || null,
    discount_value: form.discount_value,
    minimum_spend: form.minimum_spend || "0.00",
    usage_limit: form.usage_limit === "" ? null : Number(form.usage_limit),
    starts_at: form.starts_at
      ? new Date(form.starts_at).toISOString()
      : null,
    expires_at: form.expires_at
      ? new Date(form.expires_at).toISOString()
      : null,
  };
}

export default function CouponsPage({ businessId }) {
  const [coupons, setCoupons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingCoupon, setEditingCoupon] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const loadCoupons = useCallback(async () => {
    if (!businessId) {
      setCoupons([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await getCoupons(businessId);
      setCoupons(Array.isArray(data) ? data : data?.data ?? []);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to load coupons."
      );
    } finally {
      setLoading(false);
    }
  }, [businessId]);

  useEffect(() => {
    loadCoupons();
  }, [loadCoupons]);

  function resetForm() {
    setForm(emptyForm);
    setEditingCoupon(null);
    setShowForm(false);
  }

  function startEditing(coupon) {
    setEditingCoupon(coupon);
    setForm({
      code: coupon.code ?? "",
      description: coupon.description ?? "",
      discount_type: coupon.discount_type ?? "percentage",
      discount_value: String(coupon.discount_value ?? ""),
      minimum_spend: String(coupon.minimum_spend ?? "0.00"),
      usage_limit: coupon.usage_limit ?? "",
      starts_at: toDateTimeLocal(coupon.starts_at),
      expires_at: toDateTimeLocal(coupon.expires_at),
      is_active: Boolean(coupon.is_active),
    });
    setError("");
    setSuccess("");
    setShowForm(true);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const payload = preparePayload(form);

      if (editingCoupon) {
        await updateCoupon(businessId, editingCoupon.id, payload);
        setSuccess("Coupon updated successfully.");
      } else {
        await createCoupon(businessId, payload);
        setSuccess("Coupon created successfully.");
      }

      resetForm();
      await loadCoupons();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to save coupon. Check the details."
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(coupon) {
    if (!window.confirm(`Delete coupon "${coupon.code}"?`)) return;

    setError("");
    setSuccess("");

    try {
      await deleteCoupon(businessId, coupon.id);
      setSuccess("Coupon deleted successfully.");
      await loadCoupons();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to delete coupon."
      );
    }
  }

  function updateField(event) {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  if (!businessId) {
    return (
      <p className="text-slate-600">Select a business to manage coupons.</p>
    );
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Coupon Management
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Create and manage promotional discounts for your customers.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            if (showForm) {
              resetForm();
            } else {
              setForm(emptyForm);
              setEditingCoupon(null);
              setError("");
              setSuccess("");
              setShowForm(true);
            }
          }}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          {showForm ? "Cancel" : "Add Coupon"}
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

      {success && (
        <div
          role="status"
          className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
        >
          {success}
        </div>
      )}

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
        >
          <h2 className="text-lg font-semibold text-slate-900">
            {editingCoupon ? "Edit Coupon" : "New Coupon"}
          </h2>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Coupon code *
              </label>
              <input
                name="code"
                value={form.code}
                onChange={updateField}
                required
                maxLength={50}
                placeholder="WELCOME10"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm uppercase focus:border-slate-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Discount type *
              </label>
              <select
                name="discount_type"
                value={form.discount_type}
                onChange={updateField}
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
              >
                <option value="percentage">Percentage (%)</option>
                <option value="fixed">Fixed amount</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Discount value *
              </label>
              <input
                name="discount_value"
                type="number"
                min="0.01"
                step="0.01"
                max={form.discount_type === "percentage" ? "100" : undefined}
                value={form.discount_value}
                onChange={updateField}
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Minimum spend
              </label>
              <input
                name="minimum_spend"
                type="number"
                min="0"
                step="0.01"
                value={form.minimum_spend}
                onChange={updateField}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Usage limit
              </label>
              <input
                name="usage_limit"
                type="number"
                min="1"
                step="1"
                value={form.usage_limit}
                onChange={updateField}
                placeholder="Unlimited"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Description
              </label>
              <input
                name="description"
                value={form.description}
                onChange={updateField}
                placeholder="Welcome discount"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Starts at
              </label>
              <input
                name="starts_at"
                type="datetime-local"
                value={form.starts_at}
                onChange={updateField}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Expires at
              </label>
              <input
                name="expires_at"
                type="datetime-local"
                min={form.starts_at || undefined}
                value={form.expires_at}
                onChange={updateField}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
              />
            </div>

            <label className="flex items-center gap-3 self-end rounded-lg border border-slate-200 p-3 text-sm font-medium text-slate-700">
              <input
                name="is_active"
                type="checkbox"
                checked={form.is_active}
                onChange={updateField}
                className="h-4 w-4 rounded border-slate-300"
              />
              Coupon is active
            </label>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving
                ? "Saving..."
                : editingCoupon
                  ? "Save Changes"
                  : "Create Coupon"}
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="rounded-lg border border-slate-300 px-5 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Total coupons</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {coupons.length}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Active coupons</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {coupons.filter((coupon) => coupon.is_active).length}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Total redemptions</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">
            {coupons.reduce(
              (total, coupon) => total + Number(coupon.usage_count || 0),
              0
            )}
          </p>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <h2 className="font-semibold text-slate-900">Your coupons</h2>
        </div>

        {loading ? (
          <p className="p-6 text-sm text-slate-500">Loading coupons...</p>
        ) : coupons.length === 0 ? (
          <div className="p-8 text-center">
            <p className="font-medium text-slate-700">No coupons yet</p>
            <p className="mt-1 text-sm text-slate-500">
              Create your first coupon to start offering discounts.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Coupon</th>
                  <th className="px-5 py-3 font-medium">Discount</th>
                  <th className="px-5 py-3 font-medium">Minimum spend</th>
                  <th className="px-5 py-3 font-medium">Usage</th>
                  <th className="px-5 py-3 font-medium">Expiry</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {coupons.map((coupon) => (
                  <tr key={coupon.id} className="hover:bg-slate-50">
                    <td className="px-5 py-4">
                      <p className="font-semibold text-slate-900">
                        {coupon.code}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        {coupon.description || "No description"}
                      </p>
                    </td>
                    <td className="px-5 py-4 font-medium text-slate-800">
                      {coupon.discount_type === "percentage"
                        ? `${coupon.discount_value}%`
                        : coupon.discount_value}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {coupon.minimum_spend ?? "0.00"}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {coupon.usage_count ?? 0}
                      {" / "}
                      {coupon.usage_limit ?? "Unlimited"}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {coupon.expires_at
                        ? new Date(coupon.expires_at).toLocaleDateString()
                        : "No expiry"}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
                          coupon.is_active
                            ? "bg-green-100 text-green-700"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {coupon.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex gap-3">
                        <button
                          type="button"
                          onClick={() => startEditing(coupon)}
                          className="font-medium text-slate-700 hover:text-slate-950"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(coupon)}
                          className="font-medium text-red-600 hover:text-red-800"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
