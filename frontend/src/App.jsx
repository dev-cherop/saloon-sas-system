
import { BrowserRouter, Route, Routes } from "react-router-dom";

import DashboardLayout from "./layouts/DashboardLayout";
import CustomerPage from "./features/customers/CustomerPage";

const BUSINESS_ID = "e4b3aa2b-a9c0-4e52-9aa0-cf2e9dfac34e";


export default function App() {
  return (
    <BrowserRouter>
      <DashboardLayout>
        <Routes>
          <Route
            path="/"
            element={
              <div>
                <h2 className="text-2xl font-bold text-slate-900">
                  Dashboard
                </h2>

                <p className="mt-2 text-slate-500">
                  Welcome to your salon management dashboard.
                </p>
              </div>
            }
          />

          <Route
            path="/customers"
            element={<CustomerPage businessId={BUSINESS_ID} />}
          />
        </Routes>
      </DashboardLayout>
    </BrowserRouter>
  );
}