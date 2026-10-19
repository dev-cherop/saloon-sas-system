
import { useEffect, useState } from "react";
import { 
  getWorkers,
  createWorker,
  updateWorker,
  deleteWorker,
 } from "../../services/workerApi";

export default function WorkersPage({ businessId }) {
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingWorker, setEditingWorker] = useState(null);

const [form, setForm] = useState({
  first_name: "",
  last_name: "",
  phone: "",
  email: "",
  specialty: "",
});



async function handleCreateWorker(event) {
  event.preventDefault();
  setSaving(true);
  setError("");

  try {
    await createWorker(businessId, form);

    const response = await getWorkers(businessId);
    setWorkers(response.data);
    setForm({
      first_name: "",
      last_name: "",
      phone: "",
      email: "",
      specialty: "",
    });
    setShowForm(false);
  } catch {
    setError("Failed to create worker. Please check the details and try again.");
  } finally {
    setSaving(false);
  }
}


async function handleUpdateWorker(event) {
  event.preventDefault();
  setSaving(true);
  setError("");

  try {
    await updateWorker(businessId, editingWorker.id, form);

    const response = await getWorkers(businessId);
    setWorkers(response.data);
    setEditingWorker(null);
    setForm({
      first_name: "",
      last_name: "",
      phone: "",
      email: "",
      specialty: "",
    });
  } catch {
    setError("Failed to update worker. Please try again.");
  } finally {
    setSaving(false);
  }
}


  useEffect(() => {
    let cancelled = false;

    async function loadWorkers() {
      setLoading(true);
      setError("");

      try {
        const response = await getWorkers(businessId);
        if (!cancelled) {
          setWorkers(response.data);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to load workers. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    if (businessId) {
      loadWorkers();
    }

    return () => {
      cancelled = true;
    };
  }, [businessId]);

  if (loading) {
    return <p className="text-slate-500">Loading workers...</p>;
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Workers Management
        </h1>
        
        <p className="mt-1 text-sm text-slate-500">
          Manage your salon team and their specialties.
        </p>
      </div>

      <button
  type="button"
  onClick={() => {
  setShowForm(!showForm);
  setEditingWorker(null);
  setForm({
    first_name: "",
    last_name: "",
    phone: "",
    email: "",
    specialty: "",
  });
}}
  className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
>
  {showForm ? "Cancel" : "Add Worker"}
</button>


{showForm && (
  <form
    onSubmit={editingWorker ? handleUpdateWorker : handleCreateWorker}
    className="space-y-4 rounded-xl border border-slate-200 bg-white p-6"
  >
    <div className="grid gap-4 sm:grid-cols-2">
      {[
        ["first_name", "First name"],
        ["last_name", "Last name"],
        ["phone", "Phone"],
        ["email", "Email"],
        ["specialty", "Specialty"],
      ].map(([name, label]) => (
        <div key={name}>
          <label className="mb-1 block text-sm font-medium text-slate-700">
            {label}
          </label>
          <input
            name={name}
            type={name === "email" ? "email" : "text"}
            required={["first_name", "last_name"].includes(name)}
            value={form[name]}
            onChange={(event) =>
              setForm({ ...form, [name]: event.target.value })
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
          />
        </div>
      ))}
    </div>

    <button
      type="submit"
      disabled={saving}
      className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
    >
     {saving
  ? "Saving..."
  : editingWorker
    ? "Update Worker"
    : "Save Worker"}
    </button>
  </form>
)}


      {error && (
        <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}

      {!error && workers.length === 0 && (
        <div className="rounded-xl border border-dashed border-slate-300 p-8 text-center">
          <p className="font-medium text-slate-700">
            No workers added yet
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Add your salon team as the next step.
          </p>
        </div>
      )}

      {workers.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200 text-left">
            <thead className="bg-slate-50">
              <tr>
                {["Name", "Phone", "Email", "Specialty", "Status", "Actions"].map(
                  (heading) => (
                    <th
                      key={heading}
                      className="px-4 py-3 text-xs font-semibold uppercase text-slate-500"
                    >
                      {heading}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {workers.map((worker) => (
                <tr key={worker.id}>
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {worker.first_name} {worker.last_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">
                    {worker.phone || "—"}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">
                    {worker.email || "—"}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">
                    {worker.specialty || "—"}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
                      {worker.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>

<td className="px-4 py-3">
  <button
    type="button"
    onClick={() => {
      setEditingWorker(worker);
      setForm({
        first_name: worker.first_name || "",
        last_name: worker.last_name || "",
        phone: worker.phone || "",
        email: worker.email || "",
        specialty: worker.specialty || "",
      });
      setShowForm(true);
    }}
    className="text-sm font-medium text-blue-700 hover:text-blue-900"
  >
    Edit
  </button>

<button
  type="button"
  onClick={async () => {
    if (!window.confirm("Are you sure you want to delete this worker?")) {
      return;
    }

    try {
      await deleteWorker(businessId, worker.id);
      setWorkers((current) =>
        current.filter((item) => item.id !== worker.id)
      );
      setError("");
    } catch {
      setError("Failed to delete worker. Please try again.");
    }
  }}
  className="ml-3 text-sm font-medium text-red-700 hover:text-red-900"
>
  Delete
</button>

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
