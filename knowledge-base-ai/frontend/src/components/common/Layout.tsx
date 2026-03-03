/**
 * Application layout — sidebar navigation + main content area.
 * Used as the parent route element so all pages share the same chrome.
 */
import { NavLink } from 'react-router-dom';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export default function Layout() {
  return (
    <div className="layout">
      <Navbar />
      <div className="layout__body">
        <aside className="layout__sidebar">
          <nav aria-label="Main navigation">
            <ul className="nav-list">
              <li>
                <NavLink
                  to="/"
                  className={({ isActive }) =>
                    isActive ? 'nav-link nav-link--active' : 'nav-link'
                  }
                  end
                >
                  Dashboard
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/documents"
                  className={({ isActive }) =>
                    isActive ? 'nav-link nav-link--active' : 'nav-link'
                  }
                >
                  Documents
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/chat"
                  className={({ isActive }) =>
                    isActive ? 'nav-link nav-link--active' : 'nav-link'
                  }
                >
                  Chat
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/settings"
                  className={({ isActive }) =>
                    isActive ? 'nav-link nav-link--active' : 'nav-link'
                  }
                >
                  Settings
                </NavLink>
              </li>
            </ul>
          </nav>
        </aside>
        <main className="layout__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
