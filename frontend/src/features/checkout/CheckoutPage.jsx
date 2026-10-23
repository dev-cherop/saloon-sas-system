import { useEffect, useMemo, useState } from "react";
import { getCustomers } from "../../services/customerApi";
import { getServices } from "../../services/serviceApi";
import { createCheckout } from "../../services/checkoutApi";

const initialForm = {
  customer_id: "",
  coupon_code: "",
  notes: "",
};

const money = (value) =>
  `UGX ${Number(value || 0).toLocaleString("en-UG", {
    maximumFractionDigits: 2,
  })}`;

export default function CheckoutPage({ businessId }) {
  const [customers, setCustomers] = useState([]);
  const [services, setServices] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [quantities, setQuantities] = useState({});
  const [sale, setSale] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      if (!businessId) {
        setCustomers([]);
        setServices([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError("");

      try {
        const [customerData, serviceData] = await Promise.all([
          getCustomers(businessId),
          getServices(businessId),
        ]);

        if (!cancelled) {
          setCustomers(customerData);
          setServices(serviceData.filter((service) => service.is_active));
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail || "Unable to load checkout data."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadData();

    return () => {
      cancelled = true;
    };
  }, [businessId]);

  const selectedItems = useMemo(
    () =>
      services
        .filter((service) => Number(quantities[service.id] || 0) > 0)
        .map((service) => ({
          ...service,
          quantity: Number(quantities[service.id]),
          lineTotal:
            Number(service.price) * Number(quantities[service.id]),
        })),
    [services, quantities]
  );

  const subtotal = selectedItems.reduce(
    (total, item) => total + item.lineTotal,
    0
  );

  const handleQuantityChange = (serviceId, value) => {
    const quantity = value === "" ? "" : Number(value);

    setQuantities((current) => ({
      ...current,
      [serviceId]:
        quantity === "" ? "" : Math.max(0, Math.min(100, quantity)),
    }));
    setSale(null);
    setSuccess("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSale(null);

    if (!businessId) {
      setError("Select a business before creating a checkout.");
      return;
    }

    if (selectedItems.length === 0) {
      setError("Add at least one service to the sale.");
      return;
    }

    if (selectedItems.some((item) => !Number.isInteger(item.quantity) || item.quantity < 1)) {
      setError("Each selected service must have a whole-number quantity of at least 1.");
      return;
    }

    setSaving(true);

    try {
      const createdSale = await createCheckout(businessId, {
        customer_id: form.customer_id || null,
        coupon_code: form.coupon_code.trim() || null,
        notes: form.notes.trim() || null,
        items: selectedItems.map((item) => ({
          service_id: item.id,
          quantity: item.quantity,
        })),
      });

      setSale(createdSale);
      setSuccess("Sale created successfully.");
      setForm(initialForm);
      setQuantities({});
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : detail || "Unable to create the sale."
      );
    } finally {
      setSaving(false);
    }
  };

  if (!businessId) {
    return <p className="text-slate-600">Select a business to use Checkout.</p>;
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Checkout</h1>
        <p className="mt-1 text-sm text-slate-500">
          Create a sale by selecting services, quantities, and an optional coupon.
        </p>
      </header>

      {error && (
        <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {success && (
        <div role="status" className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          {success}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">Loading customers and services…</p>
      ) : (
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-6">
            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">
                Sale details
              </h2>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="checkout-customer" className="mb-1 block text-sm font-medium text-slate-700">
                    Customer (optional)
                  </label>
                  <select
                    id="checkout-customer"
                    value={form.customer_id}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        customer_id: event.target.value,
                      }))
                    }
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value="">Walk-in customer</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.first_name} {customer.last_name}
                        {customer.phone ? ` — ${customer.phone}` : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="checkout-coupon" className="mb-1 block text-sm font-medium text-slate-700">
                    Coupon code (optional)
                  </label>
                  <input
                    id="checkout-coupon"
                    value={form.coupon_code}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        coupon_code: event.target.value,
                      }))
                    }
                    maxLength={50}
                    placeholder="Enter coupon code"
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>
              </div>
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-slate-900">
                Services
              </h2>

              {services.length === 0 ? (
                <p className="text-sm text-slate-500">
                  No active services are available for this business.
                </p>
              ) : (
                <div className="space-y-3">
                  {services.map((service) => (
                    <div
                      key={service.id}
                      className="grid grid-cols-[minmax(0,1fr)_100px] items-center gap-4 rounded-lg border border-slate-200 p-3 sm:grid-cols-[minmax(0,1fr)_120px_100px]"
                    >
                      <div>
                        <p className="font-medium text-slate-900">{service.name}</p>
                        <p className="text-sm text-slate-500">
                          {service.duration_minutes} minutes
                        </p>
                        <p className="mt-1 text-sm font-medium text-slate-700 sm:hidden">
                          {money(service.price)}
                        </p>
                      </div>

                      <p className="hidden text-sm font-medium text-slate-700 sm:block">
                        {money(service.price)}
                      </p>

                      <div>
                        <label
                          htmlFor={`quantity-${service.id}`}
                          className="mb-1 block text-xs font-medium text-slate-500"
                        >
                          Quantity
                        </label>
                        <input
                          id={`quantity-${service.id}`}
                          type="number"
                          min="0"
                          max="100"
                          step="1"
                          value={quantities[service.id] ?? 0}
                          onChange={(event) =>
                            handleQuantityChange(service.id, event.target.value)
                          }
                          className="w-full rounded-lg border border-slate-300 px-2 py-2 text-sm"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <label htmlFor="checkout-notes" className="mb-2 block text-sm font-medium text-slate-700">
                Notes (optional)
              </label>
              <textarea
                id="checkout-notes"
                rows={3}
                value={form.notes}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    notes: event.target.value,
                  }))
                }
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                placeholder="Add any notes for this sale"
              />
            </section>
          </div>

          <aside className="h-fit rounded-xl border border-slate-200 bg-white p-5 shadow-sm xl:sticky xl:top-24">
            <h2 className="text-lg font-semibold text-slate-900">Order summary</h2>

            {selectedItems.length === 0 ? (
              <p className="mt-4 text-sm text-slate-500">Add services to begin.</p>
            ) : (
              <div className="mt-4 space-y-3">
                {selectedItems.map((item) => (
                  <div key={item.id} className="flex justify-between gap-3 text-sm">
                    <span className="text-slate-600">
                      {item.name} × {item.quantity}
                    </span>
                    <span className="font-medium text-slate-900">
                      {money(item.lineTotal)}
                    </span>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-5 border-t border-slate-200 pt-4">
              <div className="flex justify-between gap-3">
                <span className="text-sm text-slate-600">Estimated subtotal</span>
                <span className="font-semibold text-slate-900">{money(subtotal)}</span>
              </div>
              <p className="mt-2 text-xs text-slate-500">
                The server validates coupons and calculates the final discount and total.
              </p>
            </div>

            <button
              type="submit"
              disabled={saving || loading || selectedItems.length === 0}
              className="mt-5 w-full rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving ? "Creating sale…" : "Create sale"}
            </button>
          </aside>
        </form>
      )}

      {sale && (
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Sale confirmation</h2>
          <p className="mt-2 break-all text-sm text-slate-500">Sale ID: {sale.id}</p>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <p className="text-sm text-slate-500">Subtotal</p>
              <p className="mt-1 text-lg font-semibold">{money(sale.subtotal)}</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">Discount</p>
              <p className="mt-1 text-lg font-semibold">{money(sale.discount_amount)}</p>
            </div>
            <div>
              <p className="text-sm text-slate-500">Total due</p>
              <p className="mt-1 text-lg font-semibold">{money(sale.total_amount)}</p>
            </div>
          </div>

          <p className="mt-3 text-sm text-slate-600">
            Status: <span className="font-medium capitalize">{sale.status.replaceAll("_", " ")}</span>
          </p>
          <p className="mt-1 text-sm text-slate-500">
            This creates the sale only; record its payment separately in Payments.
          </p>
        </section>
      )}
    </div>
  );
}
