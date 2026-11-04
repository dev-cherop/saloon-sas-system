import { api } from "./api";

const payrollUrl = (businessId) =>
  `/api/v1/businesses/${businessId}/payroll`;

export const getPayroll = (businessId, params = {}) =>
  api.get(payrollUrl(businessId), { params });

export const createPayroll = (businessId, payrollData) =>
  api.post(payrollUrl(businessId), payrollData);

export const updatePayroll = (businessId, payrollId, payrollData) =>
  api.patch(`${payrollUrl(businessId)}/${payrollId}`, payrollData);

export const updatePayrollStatus = (
  businessId,
  payrollId,
  statusData
) =>
  api.patch(
    `${payrollUrl(businessId)}/${payrollId}/status`,
    statusData
  );
