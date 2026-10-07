export default function CustomerList({
  customers,
  loading,
  onEdit,
}) {
  if (loading) {
    return (
      <div className="flex items-center justify-center px-5 py-12">
        <p className="text-sm text-slate-500">
          Loading customers...
        </p>
      </div>
    );
  }

  if (customers.length === 0) {
    return (
      <div className="px-5 py-12 text-center">
        <p className="font-medium text-slate-900">
          No customers found
        </p>

        <p className="mt-1 text-sm text-slate-500">
          Add your first customer or change your search.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Customer
            </th>

            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Phone
            </th>

            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Email
            </th>

            <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              Preferences
            </th>

            <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
              Actions
            </th>
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-200 bg-white">
          {customers.map((customer) => (
            <tr
              key={customer.id}
              className="transition hover:bg-slate-50"
            >
              <td className="whitespace-nowrap px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-700">
                    {customer.first_name?.charAt(0)}
                    {customer.last_name?.charAt(0)}
                  </div>

                  <div>
                    <p className="font-medium text-slate-900">
                      {customer.first_name} {customer.last_name}
                    </p>
                  </div>
                </div>
              </td>

              <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">
                {customer.phone || "—"}
              </td>

              <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">
                {customer.email || "—"}
              </td>

              <td className="max-w-xs px-5 py-4 text-sm text-slate-600">
                <span className="line-clamp-2">
                  {customer.preferences || "—"}
                </span>
              </td>

              <td className="whitespace-nowrap px-5 py-4 text-right">
                <button
                  type="button"
                  onClick={() => onEdit(customer)}
                  className="text-sm font-semibold text-slate-700 hover:text-slate-900"
                >
                  Edit
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}