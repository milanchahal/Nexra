// pages/Dashboard.tsx - Redirects to New Jobs
import { Navigate } from 'react-router-dom';

export default function Dashboard() {
  // Redirect to new jobs page - this is the main job discovery view
  return <Navigate to="/dashboard/new-jobs" replace />;
}