# TravelMind AI UI

基于 React、TypeScript 和 Vite 的旅行灵感工作台，开发环境通过 Vite 将 `/api` 代理到 `http://127.0.0.1:8000`。

```bash
npm install
npm run dev
```

启动前端前，请先在项目根目录启动 FastAPI：

```bash
uv run uvicorn main:app --reload
```

生产构建：

```bash
npm run build
```
