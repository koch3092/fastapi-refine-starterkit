# 仓库指南

## 目录结构与模块组织
- `src/` 存放 React + Refine 应用。`src/index.tsx` 启动应用，`src/App.tsx` 定义路由与资源。
- `src/pages/<feature>/` 按功能分组路由（kebab-case 文件夹，如 `blog-posts/`），包含 `list.tsx`、`create.tsx`、`edit.tsx`、`show.tsx`，并在 `index.ts` 做 barrel 导出。
- `src/components/` 放共享 UI（如 `Header`），`src/contexts/` 放 React Context，`src/providers/` 放 Refine Providers（`auth`、`data`、`constants`）。
- `public/` 放静态资源。`index.html`、`vite.config.ts`、`tsconfig*.json` 管理构建与 TS 配置。`Dockerfile` 用于容器构建。

## 构建、测试与开发命令
- `npm run dev`：启动本地 Refine 开发服务器（热更新）。
- `npm run build`：执行 `tsc` 类型检查并构建生产包。
- `npm run start`：启动生产构建服务。
- `npm run refine`：运行 Refine CLI（脚手架或工具）。

## 编码风格与命名规范
- TypeScript + React，ESM 模块（`"type": "module"`）。
- 使用 2 空格缩进，JSX props 对齐方式与现有文件保持一致。
- 组件使用 `PascalCase`；功能目录使用 kebab-case（如 `blog-posts`）。
- 内部导入一律使用 `@` 别名（映射到 `src/`），避免相对路径。
- ESLint 配置在 `eslint.config.js`，包含 TypeScript 与 React Hooks 规则；提交前需消除警告。

## 测试规范
- 当前未配置测试框架或脚本。
- 修改后使用 `npm run build` 进行验证，并用 `npm run dev` 做简单烟测。
- 如需新增测试，请在 `package.json` 添加脚本并使用 `*.test.tsx` 命名。

## 提交与 PR 规范
- 遵循历史中的约定式提交前缀（`feat:`、`chore:`），保持简短祈使语气。
- PR 需包含清晰描述、关联 issue（如有）、UI 改动截图。
- 若涉及 `src/providers/` 或 `src/App.tsx` 的路由/资源改动，请注明 API 变更或迁移说明。

## 配置说明
- `VITE_API_URL` 表示后端 origin（例如 `http://localhost:8000`），`src/providers/constants.ts` 统一拼接 `/api/v1` 得到 Refine data provider 使用的 API base URL。
- 前端环境变量必须以 `VITE_` 开头。
- `frontend/src/client/` 为 OpenAPI 生成目录，只应包含 `index.ts`、`schemas.gen.ts`、`types.gen.ts`。不要生成或使用 `client.gen.ts`、`services.gen.ts`、`sdk.gen.ts` 等运行时请求层；运行时请求统一走 `@refinedev/simple-rest` 的 `dataProvider` / `axiosInstance`。
