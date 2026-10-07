import { useEffect, useState } from "react";

const emptyForm = {
  first_name: "",
  last_name: "",
  phone: "",
  email: "",
  preferences: "",
};

export default function CustomerForm({
  customer,
  onSubmit,
  onCancel,
  saving,
}) {
  const [formData, setFormData] = useState(emptyForm);

  useEffect(() => {
    if (customer) {
      setFormData({
        first_name: customer.first_name || "",
        last_name: customer.last_name || "",
        phone: customer.phone || "",
        email: customer.email || "",
        preferences: customer.preferences || "",
      });
    } else {
      setFormData(emptyForm);
    }
  }, [customer]);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    await onSubmit({
      first_name: formData.first_name.trim(),
      last_name: formData.last_name.trim(),
      phone: formData.phone.trim() || null,
      email: formData.email.trim() || null,
      preferences: formData.preferences.trim() || null,
    });
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900">
          {customer ? "Edit Customer" : "Add Customer"}
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          {customer
            ? "Update the customer's information."
            : "Add a new customer to your salon."}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label
              htmlFor="first_name"
              className="mb-1.5 block text-sm font-medium text-slate-700"
            >
              First name
            </label>

            <input
              id="first_name"
              name="first_name"
              type="text"
              value={formData.first_name}
              onChange={handleChange}
              required
              minLength={2}
              maxLength={100}
              className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              placeholder="Jane"
            />
          </div>

          <div>
            <label
              htmlFor="last_name"
              className="mb-1.5 block text-sm font-medium text-slate-700"
            >
              Last name
            </label>

            <input
              id="last_name"
              name="last_name"
              type="text"
              value={formData.last_name}
              onChange={handleChange}
              required
              minLength={2}
              maxLength={100}
              className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              placeholder="Doe"
            />
          </div>

          <div>
            <label
              htmlFor="phone"
              className="mb-1.5 block text-sm font-medium text-slate-700"
            >
              Phone
            </label>

            <input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              maxLength={30}
              className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              placeholder="+256 700 000 000"
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="mb-1.5 block text-sm font-medium text-slate-700"
            >
              Email
            </label>

            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              placeholder="jane@example.com"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="preferences"
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            Preferences
          </label>

          <textarea
            id="preferences"
            name="preferences"
            value={formData.preferences}
            onChange={handleChange}
            rows={4}
            placeholder="Preferred hairstyle, products, special requests..."
            className="w-full resize-none rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
          />

          <p className="mt-1.5 text-xs text-slate-500">
            Add information that will help staff provide a better service.
          </p>
        </div>

        <div className="flex flex-col-reverse gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onCancel}
            disabled={saving}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving
              ? "Saving..."
              : customer
                ? "Update Customer"
                : "Create Customer"}
          </button>
        </div>
      </form>
    </div>
  );
}