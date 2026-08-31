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

## 图片资源

旅行图片放在 `public/assets/travel`，由 React 页面使用 `/assets/travel/...` 路径引用。
当前文件来自官网原型素材包中的视觉参考裁片，用于本地原型展示；正式上线前应替换为
Unsplash 或 Pexels 的原始高清图片，并记录图片来源。

图标继续使用 `lucide-react`，不使用素材包中的图标截图。
