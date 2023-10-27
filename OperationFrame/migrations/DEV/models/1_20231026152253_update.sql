-- upgrade --
CREATE TABLE IF NOT EXISTS `department` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'id',
    `department_name` VARCHAR(30) NOT NULL  COMMENT '部门名称',
    `parent_id` INT COMMENT '父部门关系外键',
    CONSTRAINT `fk_departme_departme_ba94d121` FOREIGN KEY (`parent_id`) REFERENCES `department` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='部门表';;
CREATE TABLE IF NOT EXISTS `menu` (
    `created_at` DATETIME(6) NOT NULL  COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'id',
    `menu_name` VARCHAR(30) NOT NULL  COMMENT '菜单名称',
    `url` VARCHAR(255) NOT NULL  COMMENT '菜单链接'
) CHARACTER SET utf8mb4 COMMENT='菜单表';;
ALTER TABLE `users` ADD `department_id` INT   COMMENT '用户部门外键';
CREATE TABLE `user_menus` (`users_id` INT NOT NULL REFERENCES `users` (`id`) ON DELETE CASCADE,`menu_id` INT NOT NULL REFERENCES `menu` (`id`) ON DELETE CASCADE) CHARACTER SET utf8mb4 COMMENT='用户菜单';
ALTER TABLE `users` ADD CONSTRAINT `fk_users_departme_0f67083c` FOREIGN KEY (`department_id`) REFERENCES `department` (`id`) ON DELETE CASCADE;
-- downgrade --
ALTER TABLE `users` DROP FOREIGN KEY `fk_users_departme_0f67083c`;
DROP TABLE IF EXISTS `user_menus`;
ALTER TABLE `users` DROP COLUMN `department_id`;
DROP TABLE IF EXISTS `department`;
DROP TABLE IF EXISTS `menu`;
