# TravelMind AI UI

基于 React、TypeScript 和 Vite 的旅行规划前端，开发环境通过 Vite 将 `/api` 代理到 `http://127.0.0.1:8000`。

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
首页主视觉使用经过 Web 压缩的 Pexels 高清图片，目的地图片与对应地点保持一致。

图标统一使用 `lucide-react`，不保存图标截图或重复的本地图标资源。

## 代码结构

```text
src/
├── components/  # 公共、规划和小红书登录组件
├── data/        # 页面使用的静态目的地资料
├── layouts/     # 全站导航和页脚布局
├── router/      # React Router 路由配置
├── services/    # Axios 客户端及后端接口
├── stores/      # Zustand 全局状态与持久化边界
├── styles/      # 基础、布局、页面和响应式样式
└── views/       # 独立路由页面
```

旅行资料只来自真实后端接口。接口失败时页面展示明确错误，不生成本地模拟景点、天气或酒店数据。
