-- upgrade --
ALTER TABLE `menu` ADD `parent_id` INT   COMMENT '父菜单关系外键';
ALTER TABLE `menu` ADD CONSTRAINT `fk_menu_menu_a0892170` FOREIGN KEY (`parent_id`) REFERENCES `menu` (`id`) ON DELETE CASCADE;
-- downgrade --
ALTER TABLE `menu` DROP FOREIGN KEY `fk_menu_menu_a0892170`;
ALTER TABLE `menu` DROP COLUMN `parent_id`;
