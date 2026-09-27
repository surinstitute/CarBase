FROM oven/bun:1 AS dev

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

FROM dev AS build

COPY . .
RUN bun run build

FROM oven/bun:1 AS production

WORKDIR /app
ENV NODE_ENV=production NUXT_HOST=0.0.0.0 NUXT_PORT=3000

COPY --from=build /app/.output ./.output

EXPOSE 3000

CMD ["bun", ".output/server/index.mjs"]