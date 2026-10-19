
import { useEffect, useRef, useState } from "react";

import CustomerForm from "./CustomerForm";
import CustomerList from "./CustomerList";

import {
  createCustomer,
  getCustomers,
  updateCustomer,
} from "../../services/customerApi";

import CustomerVisitHistory from "./CustomerVisitHistory";
import CustomerLoyalty from "./CustomerLoyalty";
import { useAuth } from "../auth/authContext";


export default function CustomerPage({ businessId }) {

const { activeBusiness } = useAuth();

const loyaltyPermissions =
  activeBusiness?.id === businessId
    ? activeBusiness.permissions ?? []
    : [];

const canViewLoyalty =
  loyaltyPermissions.includes("loyalty:read");

const canRedeemLoyalty =
  loyaltyPermissions.includes("loyalty:redeem");

  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [historyCustomer, setHistoryCustomer] = useState(null);
  const [loyaltyCustomer, setLoyaltyCustomer] = useState(null);

  const requestIdRef = useRef(0);
  const activeBusinessIdRef = useRef(businessId);

  // Track the currently selected business.
  activeBusinessIdRef.current = businessId;

  async function loadCustomers(
    searchTerm = search,
    targetBusinessId = businessId
  ) {
    // Invalidate older customer-list requests.
    const requestId = ++requestIdRef.current;

    if (!targetBusinessId) {
      setCustomers([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await getCustomers(
        targetBusinessId,
        searchTerm
      );

      if (
        requestId === requestIdRef.current &&
        activeBusinessIdRef.current === targetBusinessId
      ) {
        setCustomers(data);
      }
    } catch (err) {
      if (
        requestId === requestIdRef.current &&
        activeBusinessIdRef.current === targetBusinessId
      ) {
        setCustomers([]);
        setError("Failed to load customers.");
        console.error(err);
      }
    } finally {
      if (
        requestId === requestIdRef.current &&
        activeBusinessIdRef.current === targetBusinessId
      ) {
        setLoading(false);
      }
    }
  }

  useEffect(() => {
    // Clear the previous business's data immediately.
    setCustomers([]);
    setSearch("");
    setError("");
    setShowForm(false);
    setEditingCustomer(null);
    setSaving(false);
    setHistoryCustomer(null);
    setLoyaltyCustomer(null);

    if (!businessId) {
      setLoading(false);
      return;
    }

    loadCustomers("", businessId);

    // Invalidate outstanding requests on switch or unmount.
    return () => {
      requestIdRef.current += 1;
    };

    // Reload only when the selected business changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [businessId]);

  async function handleSubmit(data) {
    const targetBusinessId = businessId;

    if (!targetBusinessId) {
      setError("Please select a business first.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      if (editingCustomer) {
        await updateCustomer(
          targetBusinessId,
          editingCustomer.id,
          data
        );
      } else {
        await createCustomer(targetBusinessId, data);
      }

      // Do not update another business's UI after an old save.
      if (
        activeBusinessIdRef.current !== targetBusinessId
      ) {
        return;
      }

      setShowForm(false);
      setEditingCustomer(null);

      await loadCustomers(search, targetBusinessId);
    } catch (err) {
      if (
        activeBusinessIdRef.current === targetBusinessId
      ) {
        setError("Failed to save customer.");
        console.error(err);
      }
    } finally {
      if (
        activeBusinessIdRef.current === targetBusinessId
      ) {
        setSaving(false);
      }
    }
  }

  function handleEdit(customer) {
    if (loading || saving) return;

    setEditingCustomer(customer);
    setShowForm(true);
  }

  function handleAddCustomer() {
    if (loading || saving) return;

    setEditingCustomer(null);
    setShowForm(true);
  }

  function handleCancel() {
    if (saving) return;

    setShowForm(false);
    setEditingCustomer(null);
  }

  function handleSearch(event) {
    event.preventDefault();
    loadCustomers(search, businessId);
  }

  if (!businessId) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
        Select a business to view its customers.
      </div>
    );
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
          onClick={handleAddCustomer}
          disabled={loading || saving}
          className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          + Add Customer
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

      {showForm && (
        <CustomerForm
          customer={editingCustomer}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
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
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                placeholder="Search by name, phone or email..."
                className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Search
            </button>
          </form>
        </div>

        {historyCustomer && (
  <CustomerVisitHistory
    key={`${businessId}-${historyCustomer.id}`}
    businessId={businessId}
    customer={historyCustomer}
    onClose={() => setHistoryCustomer(null)}
  />
)}

{loyaltyCustomer && canViewLoyalty && (
  <CustomerLoyalty
    key={`${businessId}-${loyaltyCustomer.id}`}
    businessId={businessId}
    customer={loyaltyCustomer}
    canRedeem={canRedeemLoyalty}
    onClose={() => setLoyaltyCustomer(null)}
  />
)}
        <CustomerList
  customers={customers}
  loading={loading}
  onEdit={handleEdit}
  businessId={businessId}
  onViewHistory={setHistoryCustomer}
  onViewLoyalty={setLoyaltyCustomer}
  onViewLoyalty={setLoyaltyCustomer}
canViewLoyalty={canViewLoyalty}
/>
      </div>
    </div>
  );
}