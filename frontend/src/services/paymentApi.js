import { api } from "./api";

export const getPayments = (businessId, params = {}) =>
  api.get(`/api/v1/businesses/${businessId}/payments`, { params });

export const createPayment = (businessId, paymentData) =>
  api.post(
    `/api/v1/businesses/${businessId}/payments`,
    paymentData
  );

export const getPaymentSummary = (businessId, params = {}) =>
  api.get(
    `/api/v1/businesses/${businessId}/payments/summary`,
    { params }
  );
