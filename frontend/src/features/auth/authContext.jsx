import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getCurrentUser,
  login as loginRequest,
} from "../../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [businesses, setBusinesses] = useState([]);
  const [systemPermissions, setSystemPermissions] = useState([]);
  const [activeBusiness, setActiveBusinessState] =
    useState(null);
  const [loading, setLoading] = useState(true);

  function applyContext(context) {
    setUser(context.user);
    setBusinesses(context.businesses);
    setSystemPermissions(context.system_permissions ?? []);

    setActiveBusinessState((previous) => {
      const stillAvailable = context.businesses.find(
        (business) => business.id === previous?.id
      );

      return stillAvailable ?? context.businesses[0] ?? null;
    });
  }

  async function login(email, password) {
    const data = await loginRequest(email, password);

    localStorage.setItem(
      "access_token",
      data.access_token
    );

    try {
      const context = await getCurrentUser();
      applyContext(context);
      return context;
    } catch (error) {
      localStorage.removeItem("access_token");
      throw error;
    }
  }

  function selectBusiness(businessId) {
    const business = businesses.find(
      (item) => item.id === businessId
    );

    if (business) {
      setActiveBusinessState(business);
    }
  }

  function logout() {
    localStorage.removeItem("access_token");
    setUser(null);
    setBusinesses([]);
    setSystemPermissions([]);
    setActiveBusinessState(null);
  }

  useEffect(() => {
    async function restoreSession() {
      if (!localStorage.getItem("access_token")) {
        setLoading(false);
        return;
      }

      try {
        const context = await getCurrentUser();
        applyContext(context);
      } catch {
        localStorage.removeItem("access_token");
        setUser(null);
        setBusinesses([]);
        setActiveBusinessState(null);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        businesses,
        systemPermissions,
        activeBusiness,
        selectBusiness,
        loading,
        isAuthenticated: Boolean(user),
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}