from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "source" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(32) NOT NULL  /* 名称 */,
    "uniq_id" VARCHAR(32) NOT NULL  /* 唯一ID */,
    "value" TEXT NOT NULL  /* value */,
    "init_t" INT NOT NULL  /* 初始化时间戳 */,
    "use_t" INT NOT NULL  /* 使用时间戳 */,
    "status" INT NOT NULL  DEFAULT 1 /* 状态 */,
    CONSTRAINT "uid_source_name_c8fdc4" UNIQUE ("name", "uniq_id")
);
CREATE INDEX IF NOT EXISTS "idx_source_name_c3c50e" ON "source" ("name");
CREATE INDEX IF NOT EXISTS "idx_source_uniq_id_394991" ON "source" ("uniq_id");
CREATE INDEX IF NOT EXISTS "idx_source_init_t_16cdaa" ON "source" ("init_t");
CREATE INDEX IF NOT EXISTS "idx_source_use_t_c48ace" ON "source" ("use_t");
CREATE INDEX IF NOT EXISTS "idx_source_status_d2e7d6" ON "source" ("status");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
