import { Link, useLocation } from "react-router-dom";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav className={styles.nav}>
      <span className={styles.brand}>📈 Trading Tour</span>
      <ul className={styles.links}>
        <li>
          <Link className={pathname === "/" ? styles.active : ""} to="/">
            Home
          </Link>
        </li>
        <li>
          <Link className={pathname === "/tour" ? styles.active : ""} to="/tour">
            Tour
          </Link>
        </li>
        <li>
          <Link
            className={pathname === "/dashboard" ? styles.active : ""}
            to="/dashboard"
          >
            Dashboard
          </Link>
        </li>
      </ul>
    </nav>
  );
}
