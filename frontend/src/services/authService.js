import { api } from "./api";

export async function login(email, password) {
  const response = await api.post("/api/v1/auth/login", {
    email,
    password,
  });

  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get("/api/v1/auth/me");

  return response.data;
}