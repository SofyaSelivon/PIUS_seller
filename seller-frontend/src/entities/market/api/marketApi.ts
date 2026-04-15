import { baseApi } from "../../../shared/api/baseApi";

export const marketApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    getMyMarket: builder.query({
      query: () => "/markets/my",
    }),

    updateMarket: builder.mutation({
      query: (body) => ({
        url: "/markets/my",
        method: "PATCH",
        body,
      }),
    }),

    createMarket: builder.mutation({
      query: (body) => ({
        url: "/markets/create",
        method: "POST",
        body,
      }),
    }),
  }),
});

export const {
  useGetMyMarketQuery,
  useUpdateMarketMutation,
  useCreateMarketMutation,
} = marketApi;
