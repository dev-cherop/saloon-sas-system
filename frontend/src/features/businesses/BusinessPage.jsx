
import { useEffect, useState } from "react";
import { api } from "../../services/api";
import { useAuth } from "../auth/authContext";

function getErrorMessage(err, fallback) {
  const detail = err.response?.data?.detail;
  return typeof detail === "string" ? detail : fallback;
}

export default function BusinessPage() {
  const { activeBusiness, systemPermissions } = useAuth();
  const canCreateBusiness = systemPermissions.includes("system:businesses:create");

  const [businesses, setBusinesses] = useState([]);
  const [branches, setBranches] = useState([]);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [adminEmail, setAdminEmail] = useState("");

  const [branchName, setBranchName] = useState("");
  const [branchAddress, setBranchAddress] = useState("");
  const [editingBranchId, setEditingBranchId] = useState(null);

  const [error, setError] = useState("");
  const [branchError, setBranchError] = useState("");
  const [loading, setLoading] = useState(true);
  const [branchesLoading, setBranchesLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [branchSaving, setBranchSaving] = useState(false);

  async function loadBusinesses() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/api/v1/businesses");
      setBusinesses(response.data);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load businesses.")
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadBranches(businessId) {
    if (!businessId) {
      setBranches([]);
      return;
    }

    setBranchesLoading(true);
    setBranchError("");

    try {
      const response = await api.get(
        `/api/v1/businesses/${businessId}/branches`
      );
      setBranches(response.data);
    } catch (err) {
      setBranches([]);
      setBranchError(
        getErrorMessage(err, "Unable to load branches.")
      );
    } finally {
      setBranchesLoading(false);
    }
  }

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    setBranches([]);
    setEditingBranchId(null);
    setBranchName("");
    setBranchAddress("");

    if (activeBusiness?.id) {
      loadBranches(activeBusiness.id);
    }
  }, [activeBusiness?.id]);

  async function handleBusinessSubmit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);

    try {
      await api.post("/api/v1/businesses", {
        name: name.trim(),
        email: email.trim() || null,
        admin_email: adminEmail.trim(),
      });

      setName("");
      setEmail("");
      setAdminEmail("");
      await loadBusinesses();
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Unable to create business. Check your form and API."
        )
      );
    } finally {
      setSaving(false);
    }
  }

  function resetBranchForm() {
    setEditingBranchId(null);
    setBranchName("");
    setBranchAddress("");
    setBranchError("");
  }

  function startEditingBranch(branch) {
    setEditingBranchId(branch.id);
    setBranchName(branch.name);
    setBranchAddress(branch.address || "");
    setBranchError("");
  }

  async function handleBranchSubmit(event) {
    event.preventDefault();

    if (!activeBusiness?.id) {
      setBranchError("Select an active business first.");
      return;
    }

    setBranchError("");
    setBranchSaving(true);

    const payload = {
      name: branchName.trim(),
      address: branchAddress.trim() || null,
    };

    try {
      if (editingBranchId) {
        await api.patch(
          `/api/v1/businesses/${activeBusiness.id}/branches/${editingBranchId}`,
          payload
        );
      } else {
        await api.post(
          `/api/v1/businesses/${activeBusiness.id}/branches`,
          payload
        );
      }

      resetBranchForm();
      await loadBranches(activeBusiness.id);
    } catch (err) {
      setBranchError(
        getErrorMessage(
          err,
          "Unable to save branch. Check your details and permissions."
        )
      );
    } finally {
      setBranchSaving(false);
    }
  }

  async function toggleBranchStatus(branch) {
    if (!activeBusiness?.id) return;

    setBranchError("");

    try {
      await api.patch(
        `/api/v1/businesses/${activeBusiness.id}/branches/${branch.id}`,
        { is_active: !branch.is_active }
      );

      await loadBranches(activeBusiness.id);
    } catch (err) {
      setBranchError(
        getErrorMessage(err, "Unable to update branch status.")
      );
    }
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 p-6 sm:p-8">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">
          Business Settings
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Manage registered businesses and their branches.
        </p>
      </header>

      {canCreateBusiness && (
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">
          Register a business
        </h2>

        <form
          onSubmit={handleBusinessSubmit}
          className="mt-4 grid gap-4 sm:grid-cols-2"
        >
          <div>
            <label
              htmlFor="business-name"
              className="mb-1 block text-sm font-medium text-slate-700"
            >
              Business name
            </label>
            <input
              id="business-name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              minLength={2}
              maxLength={150}
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </div>

          <div>
            <label
              htmlFor="business-email"
              className="mb-1 block text-sm font-medium text-slate-700"
            >
              Email
            </label>
            <input
              id="business-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              maxLength={255}
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </div>

          <div className="sm:col-span-2">
            <label
              htmlFor="business-admin-email"
              className="mb-1 block text-sm font-medium text-slate-700"
            >
              Existing administrator email
            </label>
            <input
              id="business-admin-email"
              type="email"
              value={adminEmail}
              onChange={(event) => setAdminEmail(event.target.value)}
              maxLength={255}
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
            />
            <p className="mt-1 text-xs text-slate-500">
              Enter the email of an existing active user. They will become
              an administrator of this business.
            </p>
          </div>

          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {saving ? "Creating..." : "Create business"}
            </button>
          </div>
        </form>

        {error && (
          <p role="alert" className="mt-3 text-sm text-red-600">
            {error}
          </p>
        )}
      </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">
          Registered businesses
        </h2>

        {loading ? (
          <p className="mt-4 text-sm text-slate-500">
            Loading businesses...
          </p>
        ) : businesses.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">
            No businesses registered yet.
          </p>
        ) : (
          <ul className="mt-4 divide-y divide-slate-100">
            {businesses.map((business) => (
              <li key={business.id} className="py-3">
                <p className="font-medium text-slate-900">
                  {business.name}
                  {activeBusiness?.id === business.id && (
                    <span className="ml-2 text-xs font-medium text-emerald-700">
                      Selected
                    </span>
                  )}
                </p>
                {business.email && (
                  <p className="text-sm text-slate-500">
                    {business.email}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">
            Branch management
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            {activeBusiness
              ? `Managing branches for ${activeBusiness.name}.`
              : "No active business selected."}
          </p>
        </div>

        {activeBusiness && (
          <form
            onSubmit={handleBranchSubmit}
            className="mt-5 grid gap-4 sm:grid-cols-2"
          >
            <div>
              <label
                htmlFor="branch-name"
                className="mb-1 block text-sm font-medium text-slate-700"
              >
                Branch name
              </label>
              <input
                id="branch-name"
                type="text"
                value={branchName}
                onChange={(event) => setBranchName(event.target.value)}
                minLength={2}
                maxLength={150}
                required
                className="w-full rounded-lg border border-slate-300 px-3 py-2"
              />
            </div>

            <div>
              <label
                htmlFor="branch-address"
                className="mb-1 block text-sm font-medium text-slate-700"
              >
                Address (optional)
              </label>
              <input
                id="branch-address"
                type="text"
                value={branchAddress}
                onChange={(event) => setBranchAddress(event.target.value)}
                maxLength={255}
                className="w-full rounded-lg border border-slate-300 px-3 py-2"
              />
            </div>

            <div className="flex flex-wrap gap-2 sm:col-span-2">
              <button
                type="submit"
                disabled={branchSaving}
                className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {branchSaving
                  ? "Saving..."
                  : editingBranchId
                    ? "Save changes"
                    : "Create branch"}
              </button>

              {editingBranchId && (
                <button
                  type="button"
                  onClick={resetBranchForm}
                  className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        )}

        {branchError && (
          <p role="alert" className="mt-3 text-sm text-red-600">
            {branchError}
          </p>
        )}

        <div className="mt-6">
          <h3 className="font-medium text-slate-900">
            Branches
          </h3>

          {branchesLoading ? (
            <p className="mt-3 text-sm text-slate-500">
              Loading branches...
            </p>
          ) : !activeBusiness ? (
            <p className="mt-3 text-sm text-slate-500">
              Select a business to manage its branches.
            </p>
          ) : branches.length === 0 ? (
            <p className="mt-3 text-sm text-slate-500">
              No branches found for this business.
            </p>
          ) : (
            <ul className="mt-3 divide-y divide-slate-100">
              {branches.map((branch) => (
                <li
                  key={branch.id}
                  className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p className="font-medium text-slate-900">
                      {branch.name}
                    </p>
                    <p className="text-sm text-slate-500">
                      {branch.address || "No address provided"}
                    </p>
                    <span
                      className={`mt-1 inline-block rounded-full px-2 py-1 text-xs font-medium ${
                        branch.is_active
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {branch.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => startEditingBranch(branch)}
                      className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleBranchStatus(branch)}
                      className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700"
                    >
                      {branch.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </main>
  );
}
