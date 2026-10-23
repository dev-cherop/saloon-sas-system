import { api } from "./api";

export async function createCheckout(businessId, checkoutData) {
  const response = await api.post(
    `/api/v1/businesses/${businessId}/checkout`,
    checkoutData
  );

  return response.data;
}

export async function getSale(businessId, saleId) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/checkout/${saleId}`
  );

  return response.data;
}
