FROM node:22.19.0-bookworm-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci --include=optional

COPY . .

ARG VITE_AMAP_JS_KEY=""
ARG VITE_AMAP_SECURITY_CODE=""

ENV VITE_AMAP_JS_KEY=${VITE_AMAP_JS_KEY} \
    VITE_AMAP_SECURITY_CODE=${VITE_AMAP_SECURITY_CODE}

RUN npm run build

FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=20s --timeout=5s --start-period=10s --retries=5 \
    CMD ["wget", "-qO-", "http://127.0.0.1/"]
