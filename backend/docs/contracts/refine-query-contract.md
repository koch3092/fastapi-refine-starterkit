# Refine 查询参数约束

## 适用范围
- 适用于 `fastapi_refine` 相关的查询配置与类型，例如 `item_filter_config`、`item_sort_config`、`item_pagination_config`、`ItemQuery` 等。

## 分层原则
- `fastapi_refine` 的类型与配置仅存在于 API 层（`app/api/`），用于解析与校验 HTTP 查询参数。
- Service 层只接收已规范化的查询结构（如 `filters`、`sorts`、`pagination` 的普通 dict/DTO），不得依赖 `fastapi_refine` 类型。
- 若需要复用，可在 API 层拆分模块，例如 `app/api/deps/refine.py`（依赖构造）或资源路由文件内的特有配置，但不下沉到 Service。

## 排序约束
- 排序解析属于通用能力，可复用统一的解析格式（例如 `sort=created_at,-name`）。
- **允许排序的字段必须按资源定义白名单**，由对应资源的 API 层配置维护。
- API 层必须校验排序字段的合法性；不允许的字段应被拒绝并返回 400（或在文档中统一约定的策略）。
- Service 层仅接收已校验的排序结构，不负责字段合法性判断。

## 过滤与分页约束
- 过滤与分页的解析与校验属于 API 层职责，可抽取通用逻辑，但**资源特有规则**必须在各自资源的配置中明确。
- Service 层只处理业务语义，不关心 HTTP 参数形式。
