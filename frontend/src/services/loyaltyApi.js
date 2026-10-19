import { api } from "./api";

export async function getLoyaltySettings(businessId) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/loyalty/settings`
  );
  return response.data;
}

export async function updateLoyaltySettings(businessId, settings) {
  const response = await api.put(
    `/api/v1/businesses/${businessId}/loyalty/settings`,
    settings
  );
  return response.data;
}


export async function getCustomerLoyalty(businessId, customerId) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/loyalty/customers/${customerId}`
  );
  return response.data;
}

export async function redeemCustomerLoyalty(
  businessId,
  customerId,
  points
) {
  const response = await api.post(
    `/api/v1/businesses/${businessId}/loyalty/customers/${customerId}/redeem`,
    { points }
  );
  return response.data;
}
