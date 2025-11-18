import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import "./index.css";

import MainLayout from "./layout/MainLayout.jsx";

// 🆕 Páginas
import Login from "./pages/Login.jsx";
import Home from "./pages/Home.jsx";
import Quotes from "./pages/Quotes.jsx";
import Users from "./pages/Users.jsx";
import CreateQuote from "./pages/CreateQuote.jsx";
import EditQuote from "./pages/EditQuote.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      {/* 🔐 Tela inicial = Login */}
      <Route path="/" element={<Login />} />

      {/* Rotas internas protegidas */}
      <Route element={<MainLayout />}>
        <Route path="/home" element={<Home />} />
        <Route path="/quotes" element={<Quotes />} />
        <Route path="/quotes/new" element={<CreateQuote />} />
        <Route path="/quotes/:id/edit" element={<EditQuote />} />
        <Route path="/users" element={<Users />} />
      </Route>
    </Routes>
  </BrowserRouter>
);
