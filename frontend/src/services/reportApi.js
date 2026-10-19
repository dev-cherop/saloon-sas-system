import {api} from "./api";

export async function getBusinessReport(businessId, startDate, endDate) {
  const response = await api.get(
    `/api/v1/businesses/${businessId}/reports/summary`,
    {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
    }
  );

  return response.data;
}
