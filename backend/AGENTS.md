# 仓库指南

## 结构速览
- `app/` 为 FastAPI 后端代码入口，`app/main.py` 创建应用，`app/api/main.py` 注册路由。
- `app/api/` 为 HTTP 接口层，`app/api/routes/` 放置具体路由，`app/api/deps/` 放置依赖注入（`common.py` 与 `refine.py`）。
- `app/services/` 为业务与 CRUD 处理层，聚合业务逻辑与数据操作。
- `app/core/` 为共享配置与基础设施，如 `config.py`、`db.py`、`security.py`。
- `app/models.py` 为数据模型定义；`app/utils.py` 为通用工具。
- `app/backend_pre_start.py`、`app/tests_pre_start.py` 为启动前检查脚本；`app/initial_data.py` 初始化数据。
- `app/alembic/` 保存迁移脚本；`alembic.ini` 为迁移配置。
- `app/email-templates/` 为邮件模板，`src/` 为 MJML 源文件，`build/` 为生成的 HTML。
- `tests/` 为 pytest 测试目录，常见子目录：`tests/api/routes/`、`tests/crud/`、`tests/scripts/`、`tests/utils/`。
- `scripts/` 提供 lint、format、test 等辅助脚本。

## 分层与契约
- API 层（`app/api/`）只处理 HTTP：路由定义、请求校验、依赖注入、响应封装；不得包含业务逻辑或 DB 操作。
- Service 层（`app/services/`）包含业务规则/权限校验/事务边界与 CRUD 数据访问，直接使用 SQLModel 访问数据库，对外暴露稳定接口。
- 数据访问统一收口在 `app/services/`，避免散落到 API 或 `app/utils.py`。
- Core 层（`app/core/`）提供配置、DB 会话、安全、外部客户端等基础设施。
- 数据模型与 Schema 当前合并在 `app/models.py`；如后续拆分再引入 `app/schemas/`。

- 依赖方向与边界：`app/api/` -> `app/services/`；`app/services/` 可依赖 `app/core/` 与 `app/models.py`；`app/core/` 不依赖上层业务代码；任何层不得绕过 `app/services/` 直接访问 DB。
- 约束补充：数据访问不得散落到 `app/utils.py` 或脚本层。
- HTTP 查询约束参见 `docs/contracts/refine-query-contract.md`。
- Refine simple-rest 约定参见 `../docs/contracts/refine-simple-rest.md`。

## 开发与运行
- `uv sync` 安装依赖；`source .venv/bin/activate` 激活虚拟环境。
- `fastapi run --reload app/main.py` 本地启动（或使用 `docker compose watch` 运行完整栈）。
- `bash scripts/lint.sh` 运行 `mypy` 与 `ruff` 检查。
- `bash scripts/format.sh` 运行 `ruff` 修复与格式化。
- `bash scripts/test.sh` 运行 pytest 覆盖率并生成 `htmlcov/index.html`。
- `docker compose exec backend bash scripts/tests-start.sh` 在容器内执行测试。

## 编码规范
- Python 3.10+，4 空格缩进，要求类型注解。
- 格式化使用 `ruff format`（兼容 Black）；Lint 使用 `ruff check`（禁止 `print`）与 `mypy --strict`。
- 模块与测试使用 snake_case；测试文件命名为 `test_*.py`。
- 每个函数必须添加 Google 风格 docstring，注释中不需要包含参数类型，重点说明用途、关键参数语义、返回值或副作用（适用时）。
- 模块文件开头不要写注释或模块级 docstring。示例：

  ```python
  def fetch_user(user_id: int) -> User:
      """Fetch a user by id.

      Args:
          user_id: The user identifier to look up.

      Returns:
          The loaded user entity.

      Raises:
          NotFoundError: When the user does not exist.
      """
  ```

## 测试指南
- 使用 pytest，测试位于 `tests/`。
- 新测试尽量放在对应区域，例如路由测试放在 `tests/api/routes/`。
- 本地覆盖率检查使用 `bash scripts/test.sh`。

## 提交与 PR 规范
- 提交信息遵循 Conventional Commits：`type: summary`（如 `feat`、`chore`），后端改动统一加 `[后端]`。
- PR 描述需包含简要说明、关联 issue、执行过的测试命令；如涉及 schema 变化需注明迁移。
- 邮件模板变更需提供前后 HTML 快照或渲染结果。

## 配置与安全提示
- 配置从 `../.env`（位于 `backend/` 上一级）加载，注意不要提交密钥。
- 生产或非本地环境需替换占位密钥（如 `changethis`）。
