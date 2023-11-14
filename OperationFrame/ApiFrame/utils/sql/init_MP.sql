/*
  此sql仅用于初始化 菜单 与 权限 数据
  若需要初始化数据库, 请用 db_mysql_init 初始化后再导入
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for menu
-- ----------------------------
DROP TABLE IF EXISTS `menu`;
CREATE TABLE `menu`  (
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `menu_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '菜单名称',
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '菜单链接',
  `parent_id` int(0) NULL DEFAULT NULL COMMENT '父菜单关系外键',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_menu_menu_a0892170`(`parent_id`) USING BTREE,
  CONSTRAINT `fk_menu_menu_a0892170` FOREIGN KEY (`parent_id`) REFERENCES `menu` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '菜单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of menu
-- ----------------------------
INSERT INTO `menu` VALUES ('2023-10-30 15:25:06.288440', '2023-11-03 14:52:44.521135', 1, '系统管理', '/view/system', NULL);
INSERT INTO `menu` VALUES ('2023-11-03 14:53:08.479923', '2023-11-14 14:04:46.197642', 2, '菜单管理', '/view/system/menu', 1);
INSERT INTO `menu` VALUES ('2023-11-03 14:53:49.051431', '2023-11-14 14:04:48.444072', 3, '用户管理', '/view/system/user', 1);
INSERT INTO `menu` VALUES ('2023-11-03 14:54:29.205394', '2023-11-14 14:05:20.054859', 4, '部门管理', '/view/system/department', 1);
INSERT INTO `menu` VALUES ('2023-11-06 15:18:52.195519', '2023-11-14 14:05:47.199888', 5, '权限管理', '/view/system/permission', 1);
INSERT INTO `menu` VALUES ('2023-11-14 14:06:17.511278', '2023-11-14 14:06:17.511278', 6, '角色管理', '/view/system/role', 1);
INSERT INTO `menu` VALUES ('2023-11-14 14:20:57.359544', '2023-11-14 14:20:57.359544', 7, '首页', '/view/home', NULL);

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`  (
  `created_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `permission_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '权限名称',
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '权限描述',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '权限状态(False:禁用,True:启用)',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '权限表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of permissions
-- ----------------------------
INSERT INTO `permissions` VALUES ('2023-10-08 10:59:29.807009', '2023-11-14 15:07:49.514250', 1, 'user_get', '查询user资源', 1);
INSERT INTO `permissions` VALUES ('2023-10-09 11:18:21.609170', '2023-11-14 14:08:15.829612', 2, 'user_update', '修改user资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-02 02:40:53.556156', '2023-11-14 14:08:17.298144', 3, 'user_create', '创建user资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-03 14:59:06.786220', '2023-11-14 14:08:19.022208', 4, 'user_delete', '删除user资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:08:58.444761', '2023-11-14 15:07:46.382239', 5, 'role_get', '查询role资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:09:28.963534', '2023-11-14 14:09:28.963534', 6, 'role_update', '修改role资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:09:44.425022', '2023-11-14 14:09:44.425022', 7, 'role_create', '创建user资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:10:00.228630', '2023-11-14 14:10:00.228630', 8, 'role_delete', '删除role资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:10:28.811225', '2023-11-14 15:07:43.270596', 9, 'menu_get', '查询menu资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:10:58.048352', '2023-11-14 14:10:58.048352', 10, 'menu_update', '修改menu资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:11:25.875530', '2023-11-14 14:11:25.875530', 11, 'menu_create', '创建menu资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:11:42.630573', '2023-11-14 14:11:42.630573', 12, 'menu_delete', '删除menu资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:12:28.594708', '2023-11-14 15:07:40.257026', 13, 'department_get', '查询department资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:12:49.900053', '2023-11-14 14:12:49.900053', 14, 'department_update', '修改department资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:13:12.818875', '2023-11-14 14:13:12.818875', 15, 'department_create', '创建department资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:13:39.321461', '2023-11-14 14:13:39.321461', 16, 'department_delete', '删除department资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:14:09.240072', '2023-11-14 14:14:09.240072', 17, 'permission_get', '查询permission资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:14:32.546808', '2023-11-14 14:14:32.546808', 18, 'permission_update', '修改permission资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:14:55.473716', '2023-11-14 14:14:55.473716', 19, 'permission_create', '创建permission资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:15:13.461868', '2023-11-14 14:15:13.461868', 20, 'permission_delete', '删除permission资源', 1);
INSERT INTO `permissions` VALUES ('2023-11-14 14:25:27.130975', '2023-11-14 14:25:27.130975', 21, 'home_get', '查询首页资源', 1);

SET FOREIGN_KEY_CHECKS = 1;
