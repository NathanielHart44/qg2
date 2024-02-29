import { ElementType, Suspense, lazy } from 'react';
import { Navigate, useRoutes } from 'react-router-dom';
// import { PATH_AFTER_LOGIN } from 'src/config';
// pages
import NotFound from 'src/pages/NotFound';
import GuestGuard from 'src/guards/GuestGuard';
import AuthGuard from 'src/guards/AuthGuard';
import { AdminGuard } from 'src/guards/ModeratorGuard';

import LoadingScreen from 'src/components/base/LoadingScreen';

// ----------------------------------------------------------------------

const Loadable = (Component: ElementType) => (props: any) => {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Component {...props} />
    </Suspense>
  );
};

function withAuthGuard(element: JSX.Element) { return <AuthGuard>{element}</AuthGuard> };
function withAdminGuard(element: JSX.Element) { return <AdminGuard>{element}</AdminGuard> };
function withGuestGuard(element: JSX.Element) { return <GuestGuard>{element}</GuestGuard> }

export default function Router() {
  return useRoutes([
    {
      path: 'auth',
      children: [
        { path: 'login', element: (withGuestGuard(<Login />)) },
        { path: 'register', element: (withGuestGuard(<Register />)) },
      ],
    },
    {
      path: '',
      children: [
        // { element: withAuthGuard(<Navigate to={PATH_AFTER_LOGIN} replace />), index: true },
        { path: 'landing', element: withGuestGuard(<LandingPage />) },
        { path: 'home', element: withAuthGuard(<Home />) },
        {
          path: 'test',
          element: withGuestGuard(<Test />),
          children: [
            { path: ':gameID', element: withGuestGuard(<Test />) },
          ],
        },
        {
          path: 'game',
          element: withAuthGuard(<Game />),
          children: [
            { path: ':gameID', element: withAuthGuard(<Game />) },
            { path: ':gameID/:lc', element: withAuthGuard(<Game />) }
          ],
        },
        { path: 'admin', element: withAdminGuard(<AdminPage />) },
        
        { path: 'profile', element: withAuthGuard(<ProfilePage />) },
        { path: '404', element: <NotFound /> },
        { path: '*', element: <Navigate to="/404" replace /> },
      ],
    },
    {
      path: '/',
      children: [
        { element: <Navigate to="/landing" replace />, index: true },
      ],
    },
    { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}

const LandingPage = Loadable(lazy(() => import('src/pages/LandingPage')));
const Home = Loadable(lazy(() => import('src/pages/Home')));
const Game = Loadable(lazy(() => import('src/pages/Game')));
const Login = Loadable(lazy(() => import('src/pages/Login')));
const Register = Loadable(lazy(() => import('src/pages/Register')));
const AdminPage = Loadable(lazy(() => import('src/pages/AdminPage')));
const ProfilePage = Loadable(lazy(() => import('src/pages/ProfilePage')));
const Test = Loadable(lazy(() => import('src/pages/Test')));