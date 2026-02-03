import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "./contexts/AuthProvider.jsx";

import "./index.css";

import MainLayout from "./layout/MainLayout.jsx";
import PrivateRoute from "./components/PrivateRoute.jsx";
import AdminRoute from "./components/AdminRoute.jsx";

import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Home from "./pages/Home.jsx";
import Quotes from "./pages/Quotes.jsx";
import Users from "./pages/Users.jsx";
import CreateQuote from "./pages/CreateQuote.jsx";
import EditQuote from "./pages/EditQuote.jsx";
import VerifyInstructions from "./pages/VerifyInstructions";
import VerifySuccess from "./pages/VerifySuccess";
import VerifyError from "./pages/VerifyError";
import VerifyEmail from "./pages/VerifyEmail.jsx";
import Preferences from "./pages/Preferences.jsx";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Habits from "./pages/Habits.jsx";
import CreateHabit from "./pages/CreateHabit.jsx";
import EditHabit from "./pages/EditHabit.jsx";
import ReadingList from "./pages/ReadingList.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <>
    {/* 🔔 Toast global */}
    <Toaster
      position="top-right"
      gutter={12}
      toastOptions={{
        duration: 4000,
        style: {
          fontSize: "14px",
        },
      }}
    />

    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Rotas públicas */}
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-instructions" element={<VerifyInstructions />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/verify-success" element={<VerifySuccess />} />
          <Route path="/verify-error" element={<VerifyError />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />

          {/* Rotas protegidas */}
          <Route
            element={
              <PrivateRoute>
                <MainLayout />
              </PrivateRoute>
            }
          >
            <Route path="/home" element={<Home />} />
            <Route path="/quotes" element={<Quotes />} />
            <Route path="/quotes/new" element={<CreateQuote />} />
            <Route path="/quotes/:id/edit" element={<EditQuote />} />
            <Route path="/habits" element={<Habits />} />
            <Route path="/habits/new" element={<CreateHabit />} />
            <Route path="/habits/:id/edit" element={<EditHabit />} />
            <Route path="/reading-list" element={<ReadingList />} />
            <Route path="/preferences" element={<Preferences />} />

            <Route
              path="/users"
              element={
                <AdminRoute>
                  <Users />
                </AdminRoute>
              }
            />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </>,
);
