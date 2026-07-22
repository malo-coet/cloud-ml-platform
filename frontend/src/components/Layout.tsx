import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import styles from "./Layout.module.css";

const NAV = [
  { to: "/datasets", label: "Datasets" },
  { to: "/experiments", label: "Experiments" },
  { to: "/models", label: "Models" },
  { to: "/deployments", label: "Deployments" },
];

export function Layout() {
  const { user, logout } = useAuth();
  const initials = (user?.full_name ?? "?")
    .split(" ")
    .map((part) => part[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <span className={styles.logo} />
          Cloud ML
        </div>

        <nav className={styles.nav}>
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.link} ${isActive ? styles.active : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className={styles.footer}>
          <NavLink
            to="/profile"
            className={({ isActive }) => `${styles.user} ${isActive ? styles.active : ""}`}
          >
            <span className={styles.avatar}>{initials}</span>
            <span className={styles.userMeta}>
              <span className={styles.userName}>{user?.full_name}</span>
              <span className={styles.userRole}>{user?.role}</span>
            </span>
          </NavLink>
          <button className={styles.logout} onClick={logout} title="Sign out">
            Sign out
          </button>
        </div>
      </aside>

      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
