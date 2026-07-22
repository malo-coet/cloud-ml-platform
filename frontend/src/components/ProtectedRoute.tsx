import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { Loading } from "./States";

export function ProtectedRoute() {
  const { user, loading } = useAuth();

  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}
