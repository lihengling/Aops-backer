-- upgrade --
ALTER TABLE `permissions` DROP COLUMN `parent_id`;
-- downgrade --
ALTER TABLE `permissions` ADD `parent_id` INT NOT NULL  COMMENT '父id' DEFAULT 0;
