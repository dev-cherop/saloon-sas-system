import { useEffect, useState } from "react";
import {
  getLoyaltySettings,
  updateLoyaltySettings,
} from "../../services/loyaltyApi";

export default function LoyaltySettingsPage({ businessId, permissions = [] }) {
  const canManage = permissions.includes("loyalty:manage");

  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadSettings() {
      setLoading(true);
      setError("");
      setMessage("");
      setSettings(null);

      try {
        const data = await getLoyaltySettings(businessId);
        if (!cancelled) setSettings(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail || "Could not load loyalty settings."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    if (businessId) loadSettings();

    return () => {
      cancelled = true;
    };
  }, [businessId]);

  function updateField(field, value) {
    setSettings((current) => ({ ...current, [field]: value }));
    setMessage("");
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!canManage || !settings) return;

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const saved = await updateLoyaltySettings(businessId, {
        enabled: settings.enabled,
        spend_per_point: settings.spend_per_point,
        redemption_value: settings.redemption_value,
        minimum_redemption_points: Number(
          settings.minimum_redemption_points
        ),
      });

      setSettings(saved);
      setMessage("Loyalty settings saved successfully.");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Could not save loyalty settings."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="p-6 text-sm text-slate-500">Loading loyalty settings...</p>;
  }

  if (!settings) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-600">{error || "Settings are unavailable."}</p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="mt-3 rounded-lg border px-4 py-2 text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  const inputClass =
    "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100 disabled:bg-slate-100";

  return (
    <div className="mx-auto max-w-3xl p-4 sm:p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">
          Loyalty Settings
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Configure how customers earn and redeem loyalty points for this business.
        </p>
      </div>

      {error && (
        <div role="alert" className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {message && (
        <div role="status" className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">
          {message}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="font-semibold text-slate-900">Loyalty programme</h2>
            <p className="mt-1 text-sm text-slate-500">
              Turn point earning and redemption on or off.
            </p>
          </div>

          <label className="flex shrink-0 items-center gap-2 text-sm font-medium">
            <input
              type="checkbox"
              checked={settings.enabled}
              disabled={!canManage || saving}
              onChange={(event) => updateField("enabled", event.target.checked)}
              className="h-4 w-4 rounded border-slate-300"
            />
            Enabled
          </label>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block text-sm font-medium text-slate-700">
            Spend required per point
            <input
              type="number"
              min="0.01"
              step="0.01"
              required
              value={settings.spend_per_point}
              disabled={!canManage || saving}
              onChange={(event) =>
                updateField("spend_per_point", event.target.value)
              }
              className={inputClass}
            />
            <span className="mt-1 block text-xs font-normal text-slate-500">
              Currency spent to earn one point.
            </span>
          </label>

          <label className="block text-sm font-medium text-slate-700">
            Redemption value per point
            <input
              type="number"
              min="0.01"
              step="0.01"
              required
              value={settings.redemption_value}
              disabled={!canManage || saving}
              onChange={(event) =>
                updateField("redemption_value", event.target.value)
              }
              className={inputClass}
            />
            <span className="mt-1 block text-xs font-normal text-slate-500">
              Currency value of one redeemed point.
            </span>
          </label>

          <label className="block text-sm font-medium text-slate-700 sm:col-span-2">
            Minimum points required for redemption
            <input
              type="number"
              min="1"
              step="1"
              required
              value={settings.minimum_redemption_points}
              disabled={!canManage || saving}
              onChange={(event) =>
                updateField("minimum_redemption_points", event.target.value)
              }
              className={inputClass}
            />
          </label>
        </div>

        {canManage ? (
          <div className="flex justify-end border-t border-slate-100 pt-4">
            <button
              type="submit"
              disabled={saving}
             className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              
            >
              {saving ? "Saving..." : "Save settings"}
            </button>
          </div>
        ) : (
          <p className="border-t border-slate-100 pt-4 text-sm text-slate-500">
            You have read-only access to these settings.
          </p>
        )}
      </form>
    </div>
  );
}