import { api } from "./api";

export const getAppointments = (businessId) =>
  api.get(`/api/v1/businesses/${businessId}/appointments`);

export const getAppointment = (businessId, appointmentId) =>
  api.get(
    `/api/v1/businesses/${businessId}/appointments/${appointmentId}`
  );

export const createAppointment = (businessId, appointmentData) =>
  api.post(
    `/api/v1/businesses/${businessId}/appointments`,
    appointmentData
  );

export const updateAppointment = (businessId, appointmentId, appointmentData) =>
  api.patch(
    `/api/v1/businesses/${businessId}/appointments/${appointmentId}`,
    appointmentData
  );

export const deleteAppointment = (businessId, appointmentId) =>
  api.delete(
    `/api/v1/businesses/${businessId}/appointments/${appointmentId}`
  );
