
import { api } from "./api";

export async function getExpenses(businessId, filters = {}) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/expenses`,
    { params: filters }
  );
  return response.data;
}

export async function createExpense(businessId, expense) {
  const response = await api.post(
    `/api/v1/businesses/${businessId}/expenses`,
    expense
  );
  return response.data;
}

export async function updateExpense(businessId, expenseId, expense) {
  const response = await api.patch(
    `/api/v1/businesses/${businessId}/expenses/${expenseId}`,
    expense
  );
  return response.data;
}

export async function deleteExpense(businessId, expenseId) {
  const response = await api.delete(
    `/api/v1/businesses/${businessId}/expenses/${expenseId}`
  );
  return response.data;
}

export async function getExpenseSummary(businessId, filters = {}) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/expenses/summary`,
    { params: filters }
  );
  return response.data;
}
