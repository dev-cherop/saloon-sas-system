
import { useEffect, useState } from "react";
import {api} from "../../services/api";

export default function BusinessPage() {
  const [businesses, setBusinesses] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  async function loadBusinesses() {
    setError("");
    setLoading(true);

    try {
      const response = await api.get("/api/v1/businesses");
      setBusinesses(response.data);
    } catch {
      setError("Unable to load businesses.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadBusinesses();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSaving(true);

    try {
      await api.post("/api/v1/businesses", {
        name,
        email: email || null,
      });

      setName("");
      setEmail("");
      await loadBusinesses();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : "Unable to create business. Check the form and API."
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main style={{ maxWidth: 800, margin: "40px auto", padding: 24 }}>
      <h1>Salon Management System</h1>
      <h2>Businesses</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="business-name">Business name</label>
          <input
            id="business-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            minLength={2}
            maxLength={150}
            required
          />
        </div>

        <div style={{ marginTop: 12 }}>
          <label htmlFor="business-email">Email</label>
          <input
            id="business-email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            maxLength={255}
          />
        </div>

        <button type="submit" disabled={saving} style={{ marginTop: 16 }}>
          {saving ? "Creating..." : "Create business"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      <h2>Registered businesses</h2>

      {loading ? (
        <p>Loading businesses...</p>
      ) : businesses.length === 0 ? (
        <p>No businesses registered yet.</p>
      ) : (
        <ul>
          {businesses.map((business) => (
            <li key={business.id}>
              <strong>{business.name}</strong>
              {business.email && <span> — {business.email}</span>}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}