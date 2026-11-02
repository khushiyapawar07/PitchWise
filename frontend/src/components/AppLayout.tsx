import { Link, NavLink, Outlet, useParams } from "react-router-dom";
import { DataBanner } from "./DataBanner";

const navClass = ({ isActive }: { isActive: boolean }) =>
  `text-sm font-medium ${isActive ? "text-white underline decoration-2 underline-offset-4" : "text-white/75 hover:text-white"}`;

export function AppLayout() {
  const { matchId } = useParams();

  return (
    <div className="min-h-screen bg-d11-bg">
      <header className="bg-d11-red shadow-lg">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <Link to="/" className="text-lg font-bold uppercase tracking-widest text-white">
            PitchWise
          </Link>
          {matchId ? (
            <nav className="flex flex-wrap gap-4">
              <NavLink to={`/match/${matchId}`} className={navClass} end>
                Venue
              </NavLink>
              <NavLink to={`/match/${matchId}/players`} className={navClass}>
                Players
              </NavLink>
              <NavLink to={`/match/${matchId}/compare`} className={navClass}>
                Compare
              </NavLink>
              <NavLink to={`/match/${matchId}/ai`} className={navClass}>
                AI
              </NavLink>
            </nav>
          ) : null}
        </div>
      </header>
      <main className="mx-auto max-w-5xl space-y-5 px-4 py-6">
        <Outlet />
        <DataBanner />
      </main>
    </div>
  );
}
