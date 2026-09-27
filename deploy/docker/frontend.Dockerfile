# ---- deps ----
FROM node:20-alpine AS deps
WORKDIR /code
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# ---- build ----
FROM node:20-alpine AS build
WORKDIR /code
COPY --from=deps /code/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ---- run ----
FROM node:20-alpine
WORKDIR /code
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
COPY --from=build /code/package.json ./package.json
COPY --from=build /code/node_modules ./node_modules
COPY --from=build /code/.next ./.next
COPY --from=build /code/public ./public

EXPOSE 3000
CMD ["npm", "run", "start"]
