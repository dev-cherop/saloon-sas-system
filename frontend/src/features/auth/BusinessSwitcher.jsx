import { useAuth } from "./authContext";

export default function BusinessSwitcher() {
  const {
    businesses,
    activeBusiness,
    selectBusiness,
  } = useAuth();

  if (businesses.length === 0) {
    return (
      <p className="text-sm text-amber-700">
        No active business memberships found.
      </p>
    );
  }

  return (
    <div className="min-w-0">
      <label
        htmlFor="active-business"
        className="block text-xs text-slate-500"
      >
        Active business
      </label>

      <select
        id="active-business"
        value={activeBusiness?.id ?? ""}
        onChange={(event) =>
          selectBusiness(event.target.value)
        }
        className="mt-1 max-w-56 rounded-md border border-slate-200 bg-white px-2 py-1.5 text-sm font-semibold text-slate-900"
      >
        {businesses.map((business) => (
          <option key={business.id} value={business.id}>
            {business.name} — {business.role}
          </option>
        ))}
      </select>
    </div>
  );
}