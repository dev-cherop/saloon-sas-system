
import { useCallback, useEffect, useState } from "react";
import {
  getCustomerLoyalty,
  redeemCustomerLoyalty,
} from "../../services/loyaltyApi";

export default function CustomerLoyalty({
  businessId,
  customer,
  onClose,
  canRedeem = false,
}) {
  const [loyalty, setLoyalty] = useState(null);
  const [points, setPoints] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [redeeming, setRedeeming] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadLoyalty = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getCustomerLoyalty(
        businessId,
        customer.id
      );

      setLoyalty(data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load loyalty information."
      );
    } finally {
      setLoading(false);
    }
  }, [businessId, customer.id]);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError("");
      setMessage("");
      setLoyalty(null);

      try {
        const data = await getCustomerLoyalty(
          businessId,
          customer.id
        );

        if (active) {
          setLoyalty(data);
        }
      } catch (err) {
        if (active) {
          setError(
            err.response?.data?.detail ||
              "Unable to load loyalty information."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      active = false;
    };
  }, [businessId, customer.id]);

  async function handleRedeem(event) {
    event.preventDefault();

    const amount = Number(points);
    const balance = Number(loyalty?.balance ?? 0);

    if (!Number.isSafeInteger(amount) || amount <= 0) {
      setError(
        "Enter a valid positive whole number of points."
      );
      return;
    }

    if (amount > balance) {
      setError(
        "Cannot redeem more points than the available balance."
      );
      return;
    }

    setRedeeming(true);
    setError("");
    setMessage("");

    try {
      // Keep this call compatible with your existing API.
      await redeemCustomerLoyalty(
        businessId,
        customer.id,
        amount
      );

      setPoints("");
      setDescription("");
      setMessage("Points redeemed successfully.");

      await loadLoyalty();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to redeem points."
      );
    } finally {
      setRedeeming(false);
    }
  }

  return (
    <section className="border-b border-slate-200 bg-slate-50 p-5">
      {/* Header */}
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">
            Loyalty — {customer.first_name}{" "}
            {customer.last_name}
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Points balance and transaction history
          </p>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-white"
        >
          Close
        </button>
      </div>

      {/* Error message */}
      {error && (
        <p
          role="alert"
          className="mb-4 text-sm text-red-700"
        >
          {error}
        </p>
      )}

      {/* Success message */}
      {message && (
        <p
          role="status"
          className="mb-4 text-sm text-green-700"
        >
          {message}
        </p>
      )}

      {/* Loading state */}
      {loading ? (
        <p className="py-4 text-sm text-slate-500">
          Loading loyalty information...
        </p>
      ) : loyalty ? (
        <>
          {/* Available points */}
          <div className="mb-5 rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-500">
              Available points
            </p>

            <p className="mt-1 text-3xl font-bold text-slate-900">
              {loyalty.balance ?? 0}
            </p>
          </div>

          {/* Redeem points */}
          {canRedeem && (
            <form
              onSubmit={handleRedeem}
              className="mb-6 grid gap-3 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-3"
            >
              <input
                type="number"
                min="1"
                max={loyalty.balance ?? 0}
                step="1"
                required
                value={points}
                onChange={(event) =>
                  setPoints(event.target.value)
                }
                placeholder="Points to redeem"
                disabled={
                  redeeming ||
                  Number(loyalty.balance ?? 0) <= 0
                }
                className="min-w-0 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />

              <input
                type="text"
                maxLength={500}
                value={description}
                onChange={(event) =>
                  setDescription(event.target.value)
                }
                placeholder="Reason (optional)"
                disabled={redeeming}
                className="min-w-0 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />

              <button
                type="submit"
                disabled={
                  redeeming ||
                  Number(loyalty.balance ?? 0) <= 0 ||
                  !points
                }
                className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {redeeming ? "Redeeming..." : "Redeem"}
              </button>
            </form>
          )}

          {/* Transaction history */}
          <h4 className="mb-3 font-semibold text-slate-900">
            Transaction history
          </h4>

          {!Array.isArray(loyalty.history) ||
          loyalty.history.length === 0 ? (
            <p className="text-sm text-slate-500">
              No loyalty transactions yet.
            </p>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                      Date
                    </th>

                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                      Type
                    </th>

                    <th className="px-4 py-3 text-right text-xs font-semibold uppercase text-slate-500">
                      Points
                    </th>

                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">
                      Description
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-200">
                  {loyalty.history.map((transaction) => (
                    <tr key={transaction.id}>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {transaction.created_at
                          ? new Date(
                              transaction.created_at
                            ).toLocaleString()
                          : "—"}
                      </td>

                      <td className="px-4 py-3 text-sm text-slate-700">
                        {transaction.transaction_type}
                      </td>

                      <td
                        className={`whitespace-nowrap px-4 py-3 text-right text-sm font-semibold ${
                          transaction.points_change < 0
                            ? "text-red-600"
                            : "text-green-700"
                        }`}
                      >
                        {transaction.points_change > 0
                          ? "+"
                          : ""}
                        {transaction.points_change}
                      </td>

                      <td className="px-4 py-3 text-sm text-slate-600">
                        {transaction.description || "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      ) : (
        <p className="py-4 text-sm text-slate-500">
          No loyalty data available.
        </p>
      )}
    </section>
  );
}