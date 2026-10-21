import { api } from "./api";

export async function getCoupons(businessId) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/coupons`
  );
  return response.data;
}

export async function createCoupon(businessId, couponData) {
  const response = await api.post(
    `/api/v1/businesses/${businessId}/coupons`,
    couponData
  );
  return response.data;
}

export async function updateCoupon(businessId, couponId, couponData) {
  const response = await api.patch(
    `/api/v1/businesses/${businessId}/coupons/${couponId}`,
    couponData
  );
  return response.data;
}

export async function deleteCoupon(businessId, couponId) {
  const response = await api.delete(
    `/api/v1/businesses/${businessId}/coupons/${couponId}`
  );
  return response.data;
}
