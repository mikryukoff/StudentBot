-- Создаем базу данных, если она не существует
CREATE DATABASE IF NOT EXISTS `student_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_0900_ai_ci;

GRANT ALL PRIVILEGES
ON student_db.*
TO 'root'@'%'
WITH GRANT OPTION;
FLUSH PRIVILEGES;

-- Используем созданную базу данных
USE `student_db`;

-- Удаляем таблицы в правильном порядке с учётом внешних ключей
DROP TABLE IF EXISTS `Grades`;
DROP TABLE IF EXISTS `WeeklySchedule`;
DROP TABLE IF EXISTS `users`;

-- Создаем таблицу users первой, так как на нее ссылаются другие таблицы
CREATE TABLE `users` (
  `chat_id` bigint NOT NULL,
  `login` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `current_week_start` date NOT NULL,
  PRIMARY KEY (`chat_id`),
  UNIQUE KEY `login_unique` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Создаем таблицу grades после users
CREATE TABLE `Grades` (
  `chat_id` bigint NOT NULL,
  `subject` varchar(200) NOT NULL,
  `component` varchar(200) NOT NULL,
  `score` varchar(200) NOT NULL,
  KEY `grades_chat_id` (`chat_id`),
  CONSTRAINT `grades_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `users` (`chat_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Создаем таблицу weeklyschedule последней
CREATE TABLE `WeeklySchedule` (
  `chat_id` bigint NOT NULL,
  `day_of_week` int NOT NULL,
  `time_slot` varchar(50) NOT NULL,
  `subject` varchar(200) NOT NULL,
  `location` varchar(200) NOT NULL,
  KEY `weekly_chat_id` (`chat_id`),
  CONSTRAINT `weeklyschedule_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `users` (`chat_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;