import { api } from "./api";

export async function getServices(businessId) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/services`
  );
  return response.data;
}

export async function createService(businessId, serviceData) {
  const response = await api.post(
    `/api/v1/businesses/${businessId}/services`,
    serviceData
  );
  return response.data;
}


export async function updateService(businessId, serviceId, serviceData) {
  const response = await api.patch(
    `/api/v1/businesses/${businessId}/services/${serviceId}`,
    serviceData
  );
  return response.data;
}

export async function deleteService(businessId, serviceId) {
  const response = await api.delete(
    `/api/v1/businesses/${businessId}/services/${serviceId}`
  );
  return response.data;
}