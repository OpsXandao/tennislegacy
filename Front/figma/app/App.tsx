import { RouterProvider } from 'react-router';
import { router } from './routes';

export default function App() {
  return (
    <>
      <div className="scanline-overlay" />
      <RouterProvider router={router} />
    </>
  );
}
