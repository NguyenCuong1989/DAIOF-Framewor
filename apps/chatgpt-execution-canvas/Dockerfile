FROM node:20-bookworm-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install --ignore-scripts
COPY tsconfig.server.json ./
COPY server ./server
COPY web ./web
RUN npm run build

FROM node:20-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --ignore-scripts && npm cache clean --force
COPY --from=build /app/dist-server ./dist-server
COPY --from=build /app/web ./web
USER node
EXPOSE 8787
CMD ["node", "dist-server/index.js"]
