
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../features/auth/authContext";

export default function PermissionRoute({ permission }) {
  const { activeBusiness, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    );
  }

  const permissions = activeBusiness?.permissions ?? [];

  if (!activeBusiness || !permissions.includes(permission)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}