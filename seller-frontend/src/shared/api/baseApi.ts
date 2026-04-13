import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const baseApi = createApi({
  reducerPath: "baseApi",
  baseQuery: fetchBaseQuery({
    baseUrl: "http://localhost:8002/api",
    credentials: "include",

    prepareHeaders: (headers) => {
      const token =
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZThkMzhjMC1mNzNjLTQ4YWMtOGEwYS0wOWNlYjQwZDc2ZGMiLCJpc1NlbGxlciI6dHJ1ZX0.0tczj0Lyk74AsoeW18NwrLEHZ9XMcitIJmkvqQ-FZl4";
        //"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI5YmE0ZWUwMS0xODZlLTQ4YTgtYTYzOC1hNjgwNGQ0ZGVmODQiLCJpc1NlbGxlciI6dHJ1ZX0.aZRdraajXo4TDSsX_wQlu7XMeBGA081R7RfjZUzDf8U";
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }

      headers.set("Content-Type", "application/json");

      return headers;
    },
  }),

  tagTypes: ["User", "Cart", "Orders", "Products"],

  endpoints: () => ({}),
});
