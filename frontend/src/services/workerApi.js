
import { api } from "./api";

const workersUrl = (businessId) =>
  `/api/v1/businesses/${businessId}/workers`;

export const getWorkers = (businessId, includeInactive = false) =>
  api.get(workersUrl(businessId), {
    params: { include_inactive: includeInactive },
  });

export const createWorker = (businessId, workerData) =>
  api.post(workersUrl(businessId), workerData);

export const updateWorker = (businessId, workerId, workerData) =>
  api.patch(`${workersUrl(businessId)}/${workerId}`, workerData);

export const deleteWorker = (businessId, workerId) =>
  api.delete(`${workersUrl(businessId)}/${workerId}`);
