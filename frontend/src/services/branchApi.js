import { api } from "./api";

export async function getBranches(businessId) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/branches`
  );
  return response.data;
}

export async function createBranch(businessId, branchData) {
  const response = await api.post(
    `/api/v1/businesses/${businessId}/branches`,
    branchData
  );
  return response.data;
}

export async function updateBranch(businessId, branchId, branchData) {
  const response = await api.patch(
    `/api/v1/businesses/${businessId}/branches/${branchId}`,
    branchData
  );
  return response.data;
}
