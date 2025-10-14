from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "api" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "path" VARCHAR(100) NOT NULL,
    "method" VARCHAR(6) NOT NULL,
    "summary" VARCHAR(500) NOT NULL,
    "tags" VARCHAR(100) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_api_created_78d19f" ON "api" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_api_updated_643c8b" ON "api" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_api_path_9ed611" ON "api" ("path");
CREATE INDEX IF NOT EXISTS "idx_api_method_a46dfb" ON "api" ("method");
CREATE INDEX IF NOT EXISTS "idx_api_summary_400f73" ON "api" ("summary");
CREATE INDEX IF NOT EXISTS "idx_api_tags_04ae27" ON "api" ("tags");
COMMENT ON COLUMN "api"."path" IS 'API路径';
COMMENT ON COLUMN "api"."method" IS '请求方法';
COMMENT ON COLUMN "api"."summary" IS '请求简介';
COMMENT ON COLUMN "api"."tags" IS 'API标签';
CREATE TABLE IF NOT EXISTS "auditlog" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL,
    "username" VARCHAR(64) NOT NULL DEFAULT '',
    "module" VARCHAR(64) NOT NULL DEFAULT '',
    "summary" VARCHAR(128) NOT NULL DEFAULT '',
    "method" VARCHAR(10) NOT NULL DEFAULT '',
    "path" VARCHAR(255) NOT NULL DEFAULT '',
    "status" INT NOT NULL DEFAULT -1,
    "response_time" INT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_auditlog_created_cc33d0" ON "auditlog" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_auditlog_updated_2f871f" ON "auditlog" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_auditlog_user_id_4b93fa" ON "auditlog" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_auditlog_usernam_b187b3" ON "auditlog" ("username");
CREATE INDEX IF NOT EXISTS "idx_auditlog_module_04058b" ON "auditlog" ("module");
CREATE INDEX IF NOT EXISTS "idx_auditlog_summary_3e27da" ON "auditlog" ("summary");
CREATE INDEX IF NOT EXISTS "idx_auditlog_method_4270a2" ON "auditlog" ("method");
CREATE INDEX IF NOT EXISTS "idx_auditlog_path_b99502" ON "auditlog" ("path");
CREATE INDEX IF NOT EXISTS "idx_auditlog_status_2a72d2" ON "auditlog" ("status");
CREATE INDEX IF NOT EXISTS "idx_auditlog_respons_8caa87" ON "auditlog" ("response_time");
COMMENT ON COLUMN "auditlog"."user_id" IS '用户ID';
COMMENT ON COLUMN "auditlog"."username" IS '用户名称';
COMMENT ON COLUMN "auditlog"."module" IS '功能模块';
COMMENT ON COLUMN "auditlog"."summary" IS '请求描述';
COMMENT ON COLUMN "auditlog"."method" IS '请求方法';
COMMENT ON COLUMN "auditlog"."path" IS '请求路径';
COMMENT ON COLUMN "auditlog"."status" IS '状态码';
COMMENT ON COLUMN "auditlog"."response_time" IS '响应时间(单位ms)';
CREATE TABLE IF NOT EXISTS "dept" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(20) NOT NULL UNIQUE,
    "desc" VARCHAR(500),
    "is_deleted" BOOL NOT NULL DEFAULT False,
    "order" INT NOT NULL DEFAULT 0,
    "parent_id" INT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_dept_created_4b11cf" ON "dept" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_dept_updated_0c0bd1" ON "dept" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_dept_name_c2b9da" ON "dept" ("name");
CREATE INDEX IF NOT EXISTS "idx_dept_is_dele_466228" ON "dept" ("is_deleted");
CREATE INDEX IF NOT EXISTS "idx_dept_order_ddabe1" ON "dept" ("order");
CREATE INDEX IF NOT EXISTS "idx_dept_parent__a71a57" ON "dept" ("parent_id");
COMMENT ON COLUMN "dept"."name" IS '部门名称';
COMMENT ON COLUMN "dept"."desc" IS '备注';
COMMENT ON COLUMN "dept"."is_deleted" IS '软删除标记';
COMMENT ON COLUMN "dept"."order" IS '排序';
COMMENT ON COLUMN "dept"."parent_id" IS '父部门ID';
CREATE TABLE IF NOT EXISTS "deptclosure" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ancestor" INT NOT NULL,
    "descendant" INT NOT NULL,
    "level" INT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS "idx_deptclosure_created_96f6ef" ON "deptclosure" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_deptclosure_updated_41fc08" ON "deptclosure" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_deptclosure_ancesto_fbc4ce" ON "deptclosure" ("ancestor");
CREATE INDEX IF NOT EXISTS "idx_deptclosure_descend_2ae8b1" ON "deptclosure" ("descendant");
CREATE INDEX IF NOT EXISTS "idx_deptclosure_level_ae16b2" ON "deptclosure" ("level");
COMMENT ON COLUMN "deptclosure"."ancestor" IS '父代';
COMMENT ON COLUMN "deptclosure"."descendant" IS '子代';
COMMENT ON COLUMN "deptclosure"."level" IS '深度';
CREATE TABLE IF NOT EXISTS "menu" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(20) NOT NULL,
    "remark" JSONB,
    "menu_type" VARCHAR(7),
    "icon" VARCHAR(100),
    "path" VARCHAR(100) NOT NULL,
    "order" INT NOT NULL DEFAULT 0,
    "parent_id" INT NOT NULL DEFAULT 0,
    "is_hidden" BOOL NOT NULL DEFAULT False,
    "component" VARCHAR(100) NOT NULL,
    "keepalive" BOOL NOT NULL DEFAULT True,
    "redirect" VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS "idx_menu_created_b6922b" ON "menu" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_menu_updated_e6b0a1" ON "menu" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_menu_name_b9b853" ON "menu" ("name");
CREATE INDEX IF NOT EXISTS "idx_menu_path_bf95b2" ON "menu" ("path");
CREATE INDEX IF NOT EXISTS "idx_menu_order_606068" ON "menu" ("order");
CREATE INDEX IF NOT EXISTS "idx_menu_parent__bebd15" ON "menu" ("parent_id");
COMMENT ON COLUMN "menu"."name" IS '菜单名称';
COMMENT ON COLUMN "menu"."remark" IS '保留字段';
COMMENT ON COLUMN "menu"."menu_type" IS '菜单类型';
COMMENT ON COLUMN "menu"."icon" IS '菜单图标';
COMMENT ON COLUMN "menu"."path" IS '菜单路径';
COMMENT ON COLUMN "menu"."order" IS '排序';
COMMENT ON COLUMN "menu"."parent_id" IS '父菜单ID';
COMMENT ON COLUMN "menu"."is_hidden" IS '是否隐藏';
COMMENT ON COLUMN "menu"."component" IS '组件';
COMMENT ON COLUMN "menu"."keepalive" IS '存活';
COMMENT ON COLUMN "menu"."redirect" IS '重定向';
CREATE TABLE IF NOT EXISTS "role" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(20) NOT NULL UNIQUE,
    "desc" VARCHAR(500)
);
CREATE INDEX IF NOT EXISTS "idx_role_created_7f5f71" ON "role" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_role_updated_5dd337" ON "role" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_role_name_e5618b" ON "role" ("name");
COMMENT ON COLUMN "role"."name" IS '角色名称';
COMMENT ON COLUMN "role"."desc" IS '角色描述';
CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "alias" VARCHAR(30),
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "phone" VARCHAR(20),
    "password" VARCHAR(128),
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_superuser" BOOL NOT NULL DEFAULT False,
    "last_login" TIMESTAMPTZ,
    "dept_id" INT
);
CREATE INDEX IF NOT EXISTS "idx_user_created_b19d59" ON "user" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_user_updated_dfdb43" ON "user" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_user_usernam_9987ab" ON "user" ("username");
CREATE INDEX IF NOT EXISTS "idx_user_alias_6f9868" ON "user" ("alias");
CREATE INDEX IF NOT EXISTS "idx_user_email_1b4f1c" ON "user" ("email");
CREATE INDEX IF NOT EXISTS "idx_user_phone_4e3ecc" ON "user" ("phone");
CREATE INDEX IF NOT EXISTS "idx_user_is_acti_83722a" ON "user" ("is_active");
CREATE INDEX IF NOT EXISTS "idx_user_is_supe_b8a218" ON "user" ("is_superuser");
CREATE INDEX IF NOT EXISTS "idx_user_last_lo_af118a" ON "user" ("last_login");
CREATE INDEX IF NOT EXISTS "idx_user_dept_id_d4490b" ON "user" ("dept_id");
COMMENT ON COLUMN "user"."username" IS '用户名称';
COMMENT ON COLUMN "user"."alias" IS '姓名';
COMMENT ON COLUMN "user"."email" IS '邮箱';
COMMENT ON COLUMN "user"."phone" IS '电话';
COMMENT ON COLUMN "user"."password" IS '密码';
COMMENT ON COLUMN "user"."is_active" IS '是否激活';
COMMENT ON COLUMN "user"."is_superuser" IS '是否为超级管理员';
COMMENT ON COLUMN "user"."last_login" IS '最后登录时间';
COMMENT ON COLUMN "user"."dept_id" IS '部门ID';
CREATE TABLE IF NOT EXISTS "account_info" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "token" VARCHAR(128) NOT NULL UNIQUE,
    "balance" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "is_active" BOOL NOT NULL DEFAULT True,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_account_inf_user_id_f50e1d" UNIQUE ("user_id")
);
CREATE INDEX IF NOT EXISTS "idx_account_inf_created_da1491" ON "account_info" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_account_inf_updated_12f8cb" ON "account_info" ("updated_at");
COMMENT ON COLUMN "account_info"."token" IS 'Token';
COMMENT ON COLUMN "account_info"."balance" IS '余额';
COMMENT ON COLUMN "account_info"."is_active" IS '是否有效';
COMMENT ON COLUMN "account_info"."user_id" IS '关联管理员';
CREATE TABLE IF NOT EXISTS "account_cost" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "item" VARCHAR(32) NOT NULL,
    "amount" DOUBLE PRECISION NOT NULL,
    "cost_type" VARCHAR(2) NOT NULL,
    "remark" VARCHAR(255) NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_account_cos_created_8a7570" ON "account_cost" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_account_cos_updated_0f6a31" ON "account_cost" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_account_cos_item_6d3853" ON "account_cost" ("item");
CREATE INDEX IF NOT EXISTS "idx_account_cos_remark_49e483" ON "account_cost" ("remark");
COMMENT ON COLUMN "account_cost"."item" IS '消费项目';
COMMENT ON COLUMN "account_cost"."amount" IS '金额';
COMMENT ON COLUMN "account_cost"."cost_type" IS '消费类型';
COMMENT ON COLUMN "account_cost"."remark" IS '备注';
COMMENT ON COLUMN "account_cost"."user_id" IS '关联用户';
CREATE TABLE IF NOT EXISTS "sync_api" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(32) NOT NULL UNIQUE,
    "host" VARCHAR(128) NOT NULL,
    "method" VARCHAR(6) NOT NULL,
    "path" VARCHAR(128) NOT NULL,
    "allow_query_params" JSONB NOT NULL,
    "allow_headers" JSONB NOT NULL,
    "main_params" JSONB NOT NULL,
    "white_list" JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_sync_api_created_cc03c7" ON "sync_api" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_sync_api_updated_eb0d4e" ON "sync_api" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_sync_api_name_e644ca" ON "sync_api" ("name");
COMMENT ON COLUMN "sync_api"."name" IS '名称';
COMMENT ON COLUMN "sync_api"."host" IS '主机';
COMMENT ON COLUMN "sync_api"."method" IS '方法';
COMMENT ON COLUMN "sync_api"."path" IS '路径';
COMMENT ON COLUMN "sync_api"."allow_query_params" IS '允许的查询参数';
COMMENT ON COLUMN "sync_api"."allow_headers" IS '允许的请求头';
COMMENT ON COLUMN "sync_api"."main_params" IS '主参数';
COMMENT ON COLUMN "sync_api"."white_list" IS '白名单';
CREATE TABLE IF NOT EXISTS "user_sync_api" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "capacity" INT NOT NULL DEFAULT 1,
    "rate" DOUBLE PRECISION NOT NULL DEFAULT 1,
    "is_active" BOOL NOT NULL DEFAULT True,
    "timeout" INT NOT NULL DEFAULT 10,
    "unit_price" DOUBLE PRECISION NOT NULL,
    "sync_api_id" BIGINT NOT NULL REFERENCES "sync_api" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_sync_a_user_id_d4564d" UNIQUE ("user_id", "sync_api_id")
);
CREATE INDEX IF NOT EXISTS "idx_user_sync_a_created_ad912b" ON "user_sync_api" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_user_sync_a_updated_c61dce" ON "user_sync_api" ("updated_at");
COMMENT ON COLUMN "user_sync_api"."capacity" IS '容量';
COMMENT ON COLUMN "user_sync_api"."rate" IS '速率';
COMMENT ON COLUMN "user_sync_api"."is_active" IS '是否有效';
COMMENT ON COLUMN "user_sync_api"."timeout" IS '超时时间';
COMMENT ON COLUMN "user_sync_api"."unit_price" IS '单价';
COMMENT ON COLUMN "user_sync_api"."sync_api_id" IS '同步API';
COMMENT ON COLUMN "user_sync_api"."user_id" IS '用户';
CREATE TABLE IF NOT EXISTS "sync_api_call" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "sync_api_name" VARCHAR(64) NOT NULL,
    "call_time" DOUBLE PRECISION NOT NULL,
    "response_size" INT NOT NULL,
    "status" VARCHAR(7) NOT NULL,
    "main_key" VARCHAR(64) NOT NULL,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_sync_api_ca_created_2dbeaa" ON "sync_api_call" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_sync_api_ca_updated_653887" ON "sync_api_call" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_sync_api_ca_sync_ap_d851e2" ON "sync_api_call" ("sync_api_name");
CREATE INDEX IF NOT EXISTS "idx_sync_api_ca_main_ke_663f09" ON "sync_api_call" ("main_key");
COMMENT ON COLUMN "sync_api_call"."sync_api_name" IS '同步API名称';
COMMENT ON COLUMN "sync_api_call"."call_time" IS '耗时';
COMMENT ON COLUMN "sync_api_call"."response_size" IS '响应大小';
COMMENT ON COLUMN "sync_api_call"."status" IS '状态';
COMMENT ON COLUMN "sync_api_call"."main_key" IS '主参数';
COMMENT ON COLUMN "sync_api_call"."user_id" IS '用户';
CREATE TABLE IF NOT EXISTS "tbcookie" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "cookie" VARCHAR(4096) NOT NULL,
    "unb" VARCHAR(32) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_tbcookie_created_23ab7d" ON "tbcookie" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_tbcookie_updated_227699" ON "tbcookie" ("updated_at");
CREATE INDEX IF NOT EXISTS "idx_tbcookie_unb_5108ee" ON "tbcookie" ("unb");
CREATE TABLE IF NOT EXISTS "role_api" (
    "role_id" BIGINT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE,
    "api_id" BIGINT NOT NULL REFERENCES "api" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_role_api_role_id_ba4286" ON "role_api" ("role_id", "api_id");
CREATE TABLE IF NOT EXISTS "role_menu" (
    "role_id" BIGINT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE,
    "menu_id" BIGINT NOT NULL REFERENCES "menu" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_role_menu_role_id_90801c" ON "role_menu" ("role_id", "menu_id");
CREATE TABLE IF NOT EXISTS "user_role" (
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "role_id" BIGINT NOT NULL REFERENCES "role" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_user_role_user_id_d0bad3" ON "user_role" ("user_id", "role_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
