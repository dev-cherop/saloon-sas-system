import { useCallback, useEffect, useMemo, useState } from "react";
import {
  getAppointments,
  createAppointment,
  updateAppointment,
  deleteAppointment,
} from "../../services/appointmentApi";
import { getCustomers } from "../../services/customerApi";
import { getServices } from "../../services/serviceApi";
import { getWorkers } from "../../services/workerApi";

const initialForm = {
  customer_id: "",
  service_id: "",
  worker_id: "",
  start_time: "",
  end_time: "",
  status: "scheduled",
  notes: "",
};

const statuses = [
  "scheduled",
  "confirmed",
  "completed",
  "cancelled",
  "no_show",
];

const fieldClass =
  "w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100";

const buttonClass =
  "rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60";

const displayError = (err, fallback) => {
  const detail = err.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(", ");
  return detail || fallback;
};

const localDateTime = (value) => {
  if (!value) return "";
  const date = new Date(value);
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
};

const apiDateTime = (value) => new Date(value).toISOString();

const formatDateTime = (value) =>
  new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });

const personName = (person) =>
  [person?.first_name, person?.last_name].filter(Boolean).join(" ") || "Unnamed";

const statusLabel = (status) =>
  status.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());

const statusClass = (status) => {
  const styles = {
    scheduled: "bg-blue-50 text-blue-700",
    confirmed: "bg-indigo-50 text-indigo-700",
    completed: "bg-green-50 text-green-700",
    cancelled: "bg-red-50 text-red-700",
    no_show: "bg-gray-100 text-gray-700",
  };
  return styles[status] || "bg-gray-100 text-gray-700";
};

const sameDay = (first, second) =>
  first.getFullYear() === second.getFullYear() &&
  first.getMonth() === second.getMonth() &&
  first.getDate() === second.getDate();

const dateHeading = (date, options = { dateStyle: "medium" }) =>
  date.toLocaleDateString(undefined, options);

export default function AppointmentsPage({ businessId }) {
  const [appointments, setAppointments] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [services, setServices] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [calendarDate, setCalendarDate] = useState(() => new Date());
  const [calendarView, setCalendarView] = useState("week");
  const [form, setForm] = useState(initialForm);

  const loadData = useCallback(async () => {
    if (!businessId) {
      setAppointments([]);
      setCustomers([]);
      setServices([]);
      setWorkers([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");
    try {
      const [appointmentsResponse, customersData, servicesData, workersResponse] =
        await Promise.all([
          getAppointments(businessId),
          getCustomers(businessId),
          getServices(businessId),
          getWorkers(businessId),
        ]);

      setAppointments(appointmentsResponse.data);
      setCustomers(customersData);
      setServices(servicesData);
      setWorkers(workersResponse.data);
    } catch (err) {
      setError(displayError(err, "Failed to load appointments."));
    } finally {
      setLoading(false);
    }
  }, [businessId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const resetForm = () => {
    setForm(initialForm);
    setEditingId(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!businessId) {
      setError("Select a business before managing appointments.");
      return;
    }
    if (new Date(form.end_time) <= new Date(form.start_time)) {
      setError("End time must be later than start time.");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        customer_id: form.customer_id,
        service_id: form.service_id,
        worker_id: form.worker_id,
        start_time: apiDateTime(form.start_time),
        end_time: apiDateTime(form.end_time),
        status: form.status,
        notes: form.notes.trim() || null,
      };

      if (editingId) {
        await updateAppointment(businessId, editingId, payload);
        setSuccess("Appointment updated successfully.");
      } else {
        await createAppointment(businessId, payload);
        setSuccess("Appointment created successfully.");
      }
      resetForm();
      await loadData();
    } catch (err) {
      setError(
        displayError(
          err,
          editingId ? "Failed to update appointment." : "Failed to create appointment."
        )
      );
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (appointment) => {
    setError("");
    setSuccess("");
    setEditingId(appointment.id);
    setForm({
      customer_id: appointment.customer_id,
      service_id: appointment.service_id,
      worker_id: appointment.worker_id,
      start_time: localDateTime(appointment.start_time),
      end_time: localDateTime(appointment.end_time),
      status: appointment.status,
      notes: appointment.notes || "",
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDelete = async (appointment) => {
    if (!window.confirm("Are you sure you want to delete this appointment?")) return;

    setError("");
    setSuccess("");
    try {
      await deleteAppointment(businessId, appointment.id);
      if (editingId === appointment.id) resetForm();
      setSuccess("Appointment deleted successfully.");
      await loadData();
    } catch (err) {
      setError(displayError(err, "Failed to delete appointment."));
    }
  };

  const handleStatusChange = async (appointment, status) => {
    setError("");
    setSuccess("");
    try {
      await updateAppointment(businessId, appointment.id, { status });
      setSuccess("Appointment status updated.");
      await loadData();
    } catch (err) {
      setError(displayError(err, "Failed to update appointment status."));
    }
  };

  const customerById = useMemo(
    () => Object.fromEntries(customers.map((item) => [item.id, item])),
    [customers]
  );
  const serviceById = useMemo(
    () => Object.fromEntries(services.map((item) => [item.id, item])),
    [services]
  );
  const workerById = useMemo(
    () => Object.fromEntries(workers.map((item) => [item.id, item])),
    [workers]
  );

  const filteredAppointments = useMemo(
    () =>
      appointments
        .filter((appointment) => {
          if (statusFilter !== "all" && appointment.status !== statusFilter) return false;
          const customer = customerById[appointment.customer_id];
          const service = serviceById[appointment.service_id];
          const worker = workerById[appointment.worker_id];
          const searchText = [
            personName(customer),
            service?.name || "",
            personName(worker),
            appointment.notes || "",
          ]
            .join(" ")
            .toLowerCase();
          return searchText.includes(search.trim().toLowerCase());
        })
        .sort((a, b) => new Date(a.start_time) - new Date(b.start_time)),
    [appointments, statusFilter, search, customerById, serviceById, workerById]
  );

  const calendarDays = useMemo(() => {
    const start = new Date(calendarDate);
    start.setHours(0, 0, 0, 0);
    if (calendarView === "week") {
      start.setDate(start.getDate() - start.getDay());
    }
    return Array.from({ length: calendarView === "week" ? 7 : 1 }, (_, index) => {
      const day = new Date(start);
      day.setDate(start.getDate() + index);
      return day;
    });
  }, [calendarDate, calendarView]);

  const moveCalendar = (amount) => {
    setCalendarDate((current) => {
      const next = new Date(current);
      next.setDate(next.getDate() + amount * (calendarView === "week" ? 7 : 1));
      return next;
    });
  };

  const calendarTitle =
    calendarView === "day"
      ? dateHeading(calendarDays[0], { weekday: "long", month: "long", day: "numeric", year: "numeric" })
      : `${dateHeading(calendarDays[0], { month: "short", day: "numeric" })} – ${dateHeading(
          calendarDays[6],
          { month: "short", day: "numeric", year: "numeric" }
        )}`;

  const upcomingCount = appointments.filter(
    (appointment) =>
      new Date(appointment.start_time) >= new Date() &&
      ["scheduled", "confirmed"].includes(appointment.status)
  ).length;

  const todayCount = appointments.filter((appointment) => {
    const date = new Date(appointment.start_time);
    return sameDay(date, new Date()) && !["cancelled", "no_show"].includes(appointment.status);
  }).length;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">Appointments</h1>
        <p className="mt-1 text-sm text-gray-500">
          Schedule appointments, manage bookings, and track their status.
        </p>
      </header>

      {error && (
        <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div role="status" className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          {success}
        </div>
      )}

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Total appointments</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{appointments.length}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Today</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{todayCount}</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-gray-500">Upcoming</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{upcomingCount}</p>
        </div>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-gray-900">
            {editingId ? "Edit appointment" : "Book an appointment"}
          </h2>
          {editingId && (
            <button type="button" onClick={resetForm} className="text-sm font-medium text-gray-600 hover:text-gray-900">
              Cancel editing
            </button>
          )}
        </div>

        {!businessId ? (
          <p className="text-sm text-gray-500">Select an active business to manage appointments.</p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div>
                <label htmlFor="customer_id" className="mb-1 block text-sm font-medium text-gray-700">Customer</label>
                <select id="customer_id" name="customer_id" value={form.customer_id} onChange={handleChange} className={fieldClass} required>
                  <option value="">Select customer</option>
                  {customers.map((customer) => <option key={customer.id} value={customer.id}>{personName(customer)}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="service_id" className="mb-1 block text-sm font-medium text-gray-700">Service</label>
                <select id="service_id" name="service_id" value={form.service_id} onChange={handleChange} className={fieldClass} required>
                  <option value="">Select service</option>
                  {services.map((service) => <option key={service.id} value={service.id}>{service.name}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="worker_id" className="mb-1 block text-sm font-medium text-gray-700">Worker</label>
                <select id="worker_id" name="worker_id" value={form.worker_id} onChange={handleChange} className={fieldClass} required>
                  <option value="">Select worker</option>
                  {workers.map((worker) => <option key={worker.id} value={worker.id}>{personName(worker)}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="start_time" className="mb-1 block text-sm font-medium text-gray-700">Start date and time</label>
                <input id="start_time" name="start_time" type="datetime-local" value={form.start_time} onChange={handleChange} className={fieldClass} required />
              </div>
              <div>
                <label htmlFor="end_time" className="mb-1 block text-sm font-medium text-gray-700">End date and time</label>
                <input id="end_time" name="end_time" type="datetime-local" value={form.end_time} onChange={handleChange} className={fieldClass} required />
              </div>
              <div>
                <label htmlFor="status" className="mb-1 block text-sm font-medium text-gray-700">Status</label>
                <select id="status" name="status" value={form.status} onChange={handleChange} className={fieldClass} required>
                  {statuses.map((status) => <option key={status} value={status}>{statusLabel(status)}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label htmlFor="notes" className="mb-1 block text-sm font-medium text-gray-700">Notes (optional)</label>
              <textarea id="notes" name="notes" value={form.notes} onChange={handleChange} rows={3} maxLength={2000} placeholder="Add any special instructions..." className={fieldClass} />
            </div>
            <button type="submit" disabled={saving} className={buttonClass}>
              {saving ? "Saving..." : editingId ? "Save changes" : "Book appointment"}
            </button>
          </form>
        )}
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Appointment calendar</h2>
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" onClick={() => setCalendarDate(new Date())} className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">Today</button>
            <button type="button" onClick={() => moveCalendar(-1)} aria-label="Previous date range" className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">←</button>
            <button type="button" onClick={() => moveCalendar(1)} aria-label="Next date range" className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">→</button>
            <select aria-label="Calendar view" value={calendarView} onChange={(event) => setCalendarView(event.target.value)} className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900">
              <option value="day">Day</option>
              <option value="week">Week</option>
            </select>
          </div>
        </div>
        <p className="mb-4 text-sm font-medium text-gray-600">{calendarTitle}</p>

        {loading ? (
          <p className="py-8 text-center text-sm text-gray-500">Loading calendar...</p>
        ) : (
          <div className={`grid gap-3 ${calendarView === "week" ? "grid-cols-1 sm:grid-cols-2 lg:grid-cols-7" : "grid-cols-1"}`}>
            {calendarDays.map((day) => {
              const dayAppointments = filteredAppointments.filter((appointment) =>
                sameDay(new Date(appointment.start_time), day)
              );
              const isToday = sameDay(day, new Date());

              return (
                <div key={day.toISOString()} className={`min-h-36 rounded-lg border p-3 ${isToday ? "border-indigo-300 bg-indigo-50/40" : "border-gray-200 bg-white"}`}>
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{dateHeading(day, { weekday: "short" })}</p>
                      <p className={`text-lg font-semibold ${isToday ? "text-indigo-700" : "text-gray-900"}`}>{dateHeading(day, { month: "short", day: "numeric" })}</p>
                    </div>
                    <span className="rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">{dayAppointments.length}</span>
                  </div>
                  <div className="space-y-2">
                    {dayAppointments.length === 0 ? (
                      <p className="py-2 text-xs text-gray-400">No appointments</p>
                    ) : (
                      dayAppointments.map((appointment) => (
                        <button key={appointment.id} type="button" onClick={() => handleEdit(appointment)} className={`block w-full rounded-md p-2 text-left text-xs hover:ring-2 hover:ring-indigo-200 ${statusClass(appointment.status)}`} title="Click to edit appointment">
                          <span className="block font-semibold">
                            {new Date(appointment.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                            {" · "}
                            {personName(customerById[appointment.customer_id])}
                          </span>
                          <span className="mt-1 block opacity-80">{serviceById[appointment.service_id]?.name || "Unavailable service"}</span>
                          <span className="mt-1 block opacity-80">{personName(workerById[appointment.worker_id])}</span>
                          <span className="mt-1 block font-medium">{statusLabel(appointment.status)}</span>
                        </button>
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
        <p className="mt-3 text-xs text-gray-500">Select an appointment card to edit its details. Search and status filters below also apply to the calendar.</p>
      </section>

      <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Appointment list</h2>
          <button type="button" onClick={loadData} disabled={loading} className="self-start rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-60">Refresh</button>
        </div>

        <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search customer, service, or worker..." aria-label="Search appointments" className={fieldClass} />
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} aria-label="Filter appointments by status" className={fieldClass}>
            <option value="all">All statuses</option>
            {statuses.map((status) => <option key={status} value={status}>{statusLabel(status)}</option>)}
          </select>
        </div>

        {loading ? (
          <p className="py-8 text-center text-sm text-gray-500">Loading appointments...</p>
        ) : filteredAppointments.length === 0 ? (
          <p className="py-8 text-center text-sm text-gray-500">No appointments found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-left">
              <thead className="bg-gray-50">
                <tr>
                  {["Customer", "Service", "Worker", "Start", "End", "Status", "Actions"].map((heading) => (
                    <th key={heading} className="whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-wide text-gray-500">{heading}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {filteredAppointments.map((appointment) => (
                  <tr key={appointment.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">{personName(customerById[appointment.customer_id])}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{serviceById[appointment.service_id]?.name || "Unavailable"}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{personName(workerById[appointment.worker_id])}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{formatDateTime(appointment.start_time)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-700">{formatDateTime(appointment.end_time)}</td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusClass(appointment.status)}`}>{statusLabel(appointment.status)}</span>
                      <label className="sr-only" htmlFor={`status-${appointment.id}`}>Change status</label>
                      <select id={`status-${appointment.id}`} value={appointment.status} onChange={(event) => handleStatusChange(appointment, event.target.value)} className="mt-2 block max-w-32 rounded border border-gray-200 px-2 py-1 text-xs">
                        {statuses.map((status) => <option key={status} value={status}>{statusLabel(status)}</option>)}
                      </select>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <div className="flex items-center gap-3">
                        <button type="button" onClick={() => handleEdit(appointment)} className="text-sm font-medium text-indigo-600 hover:text-indigo-800">Edit</button>
                        <button type="button" onClick={() => handleDelete(appointment)} className="text-sm font-medium text-red-600 hover:text-red-800">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!loading && <p className="mt-3 text-xs text-gray-500">Showing {filteredAppointments.length} of {appointments.length} appointments</p>}
      </section>
    </div>
  );
}
