import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";

import MainLayout from "./layout/MainLayout.jsx";
import Home from "./pages/Home.jsx";
import Quotes from "./pages/Quotes.jsx";
import Users from "./pages/Users.jsx";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/quotes" element={<Quotes />} />
        <Route path="/users" element={<Users />} />
      </Route>
    </Routes>
  </BrowserRouter>
);


