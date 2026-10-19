
import { useEffect, useState } from "react";
import {
  getServices,
  createService,
  updateService,
  deleteService,
} from "../../services/serviceApi";

export default function ServicesPage({ businessId }) {
  const [services, setServices] = useState([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [duration, setDuration] = useState("30");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);

  async function loadServices() {
    try {
      setError("");
      const data = await getServices(businessId);
      setServices(data);
    } catch {
      setError("Could not load services.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (businessId) loadServices();
  }, [businessId]);

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
const payload = {
  name: name.trim(),
  description: description.trim() || null,
  price,
  duration_minutes: Number(duration),
};

if (editingId) {
  const service = await updateService(
    businessId,
    editingId,
    payload
  );

  setServices((current) =>
    current.map((item) =>
      item.id === editingId ? service : item
    )
  );
    setEditingId(null);
  } else {
    const service = await createService(businessId, payload);
    setServices((current) => [...current, service]);
  }

  setName("");
  setDescription("");
  setPrice("");
  setDuration("30");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Could not create service."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Services Catalog
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage your salon services, prices, and durations.
        </p>
      </div>

      {error && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}

      <form
        onSubmit={handleSubmit}
        className="grid gap-4 rounded-xl border border-slate-200 bg-white p-5 sm:grid-cols-2"
      >
        <div>
          <label className="mb-1 block text-sm font-medium">
            Service name
          </label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            placeholder="e.g. Haircut"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">
            Price
          </label>
          <input
            required
            type="number"
            min="0"
            step="0.01"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            placeholder="0.00"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">
            Duration (minutes)
          </label>
          <input
            required
            type="number"
            min="1"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">
            Description
          </label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            placeholder="Optional"
          />
        </div>

        <div className="sm:col-span-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded-lg bg-slate-900 px-5 py-2 text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {saving
  ? "Saving..."
  : editingId
    ? "Update Service"
    : "Add Service"}
          </button>
          {editingId && (
  <button
    type="button"
    onClick={() => {
      setEditingId(null);
      setName("");
      setDescription("");
      setPrice("");
      setDuration("30");
      setError("");
    }}
    className="ml-3 rounded-lg border border-slate-300 px-5 py-2 text-slate-700 hover:bg-slate-50"
  >
    Cancel
  </button>
)}
        </div>
      </form>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        {loading ? (
          <p className="p-5 text-slate-500">Loading services...</p>
        ) : services.length === 0 ? (
          <p className="p-5 text-slate-500">
            No services added yet.
          </p>
        ) : (
          
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-5 py-3">Service</th>
                <th className="px-5 py-3">Price</th>
                <th className="px-5 py-3">Duration</th>
                <th className="px-5 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {services.map((service) => (
                <tr key={service.id}>
                  <td className="px-5 py-3">
                    <p className="font-medium text-slate-900">
                      {service.name}
                    </p>
                    {service.description && (
                      <p className="mt-1 text-slate-500">
                        {service.description}
                      </p>
                    )}
                  </td>
                  <td className="px-5 py-3">{service.price}</td>
                  <td className="px-5 py-3">
                    {service.duration_minutes} min
                  </td>
                  <td className="space-x-3 px-5 py-3">
  <button
    type="button"
    onClick={() => {
      setEditingId(service.id);
      setName(service.name);
      setDescription(service.description || "");
      setPrice(String(service.price));
      setDuration(String(service.duration_minutes));
    }}
    className="font-medium text-blue-600 hover:text-blue-800"
  >
    Edit
  </button>
  <button
  type="button"
  onClick={async () => {
    if (!window.confirm(`Delete "${service.name}"?`)) return;

    try {
      setError("");
      await deleteService(businessId, service.id);
      setServices((current) =>
        current.filter((item) => item.id !== service.id)
      );

      if (editingId === service.id) {
        setEditingId(null);
        setName("");
        setDescription("");
        setPrice("");
        setDuration("30");
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || "Could not delete service."
      );
    }
  }}
  className="font-medium text-red-600 hover:text-red-800"
>
  Delete
</button>
</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
