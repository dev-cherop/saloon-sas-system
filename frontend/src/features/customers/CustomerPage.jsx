import { useEffect, useState } from "react";

import CustomerForm from "./CustomerForm";
import CustomerList from "./CustomerList";

import {
  createCustomer,
  getCustomers,
  updateCustomer,
} from "../../services/customerApi";



export default function CustomerPage({ businessId }) {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);

  async function loadCustomers(searchTerm = search) {
    try {
      setLoading(true);
      setError("");

      const data = await getCustomers(businessId, searchTerm);
      setCustomers(data);
    } catch (err) {
      setError("Failed to load customers.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCustomers("");
  }, [businessId]);

  async function handleSubmit(data) {
    try {
      setSaving(true);
      setError("");

      if (editingCustomer) {
        await updateCustomer(businessId, editingCustomer.id, data);
      } else {
        await createCustomer(businessId, data);
      }

      setShowForm(false);
      setEditingCustomer(null);

      await loadCustomers();
    } catch (err) {
      setError("Failed to save customer.");
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  function handleEdit(customer) {
    setEditingCustomer(customer);
    setShowForm(true);
  }

  function handleAddCustomer() {
    setEditingCustomer(null);
    setShowForm(true);
  }

  function handleCancel() {
    setShowForm(false);
    setEditingCustomer(null);
  }

  function handleSearch(event) {
    event.preventDefault();
    loadCustomers(search);
  }

return (
  <div className="mx-auto max-w-7xl space-y-6">
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Customers
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Manage your salon customers and their information.
        </p>
      </div>

      <button
        type="button"
        onClick={() => {
          setEditingCustomer(null);
          setShowForm(true);
        }}
        className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
      >
        + Add Customer
      </button>
    </div>

    {error && (
      <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {error}
      </div>
    )}

    {showForm && (
      <CustomerForm
        customer={editingCustomer}
        onSubmit={handleSubmit}
        onCancel={() => {
          setShowForm(false);
          setEditingCustomer(null);
        }}
        saving={saving}
      />
    )}

    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-4 sm:p-5">
        <form
          onSubmit={handleSearch}
          className="flex flex-col gap-3 sm:flex-row"
        >
          <div className="relative flex-1">
            <input
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by name, phone or email..."
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
            />
          </div>

          <button
            type="submit"
            className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Search
          </button>
        </form>
      </div>

      <CustomerList
        customers={customers}
        loading={loading}
        onEdit={(customer) => {
          setEditingCustomer(customer);
          setShowForm(true);
        }}
      />
    </div>
  </div>
);
}