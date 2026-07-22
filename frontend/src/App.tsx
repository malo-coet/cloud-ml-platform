import { Suspense, lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Loading } from "./components/States";
import { DatasetsPage } from "./pages/DatasetsPage";
import { DeploymentsPage } from "./pages/DeploymentsPage";
import { LoginPage } from "./pages/LoginPage";
import { ModelsPage } from "./pages/ModelsPage";
import { ProfilePage } from "./pages/ProfilePage";

// Loaded on demand: this page pulls in the charting library (Recharts),
// which we keep out of the initial bundle.
const ExperimentsPage = lazy(() =>
  import("./pages/ExperimentsPage").then((m) => ({ default: m.ExperimentsPage })),
);

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/datasets" element={<DatasetsPage />} />
                <Route path="/experiments" element={<ExperimentsPage />} />
                <Route path="/models" element={<ModelsPage />} />
                <Route path="/deployments" element={<DeploymentsPage />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/datasets" replace />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
