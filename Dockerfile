FROM node:20.18.0-bookworm-slim AS node-runtime
FROM ghcr.io/astral-sh/uv:0.12.5 AS uv-runtime

FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

# 小红书签名脚本由 PyExecJS 调用，后端运行镜像必须同时提供 Node.js 与 npm。
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=uv-runtime /uv /uvx /bin/
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

WORKDIR /app

COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --frozen --no-dev --no-install-project

COPY vendor/spider_xhs/package.json vendor/spider_xhs/package-lock.json ./vendor/spider_xhs/
RUN npm ci --omit=dev --prefix vendor/spider_xhs \
    && npm cache clean --force

COPY app ./app
COPY vendor/spider_xhs ./vendor/spider_xhs
COPY main.py ./

RUN groupadd --gid 10001 travelmind \
    && useradd --uid 10001 --gid travelmind --no-create-home travelmind \
    && mkdir -p /app/data \
    && chown travelmind:travelmind /app/data

USER travelmind

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=5s --start-period=20s --retries=5 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3).read()"]

# 单进程保证管理员更新的系统内容账号会话在所有请求中保持一致。
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
