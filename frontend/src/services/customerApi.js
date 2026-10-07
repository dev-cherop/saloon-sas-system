import { api } from "./api";

export async function getCustomers(businessId, search = "") {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/customers`,
    {
      params: search ? { search } : {},
    }
  );

  return response.data;
}

export async function createCustomer(businessId, customer) {
  const response = await api.post(
    `/api/v1/businesses/${businessId}/customers`,
    customer
  );

  return response.data;
}

export async function updateCustomer(
  businessId,
  customerId,
  customer
) {
  const response = await api.patch(
    `/api/v1/businesses/${businessId}/customers/${customerId}`,
    customer
  );

  return response.data;
}

export async function getCustomer(
  businessId,
  customerId
) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/customers/${customerId}`
  );

  return response.data;
}