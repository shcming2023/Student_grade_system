CREATE TABLE `exam_sessions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(200) NOT NULL,
	`schoolYear` varchar(50) NOT NULL,
	`semester` varchar(20) NOT NULL,
	`startDate` timestamp,
	`endDate` timestamp,
	`description` text,
	`status` enum('draft','active','completed','archived') NOT NULL DEFAULT 'draft',
	`createdBy` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `exam_sessions_id` PRIMARY KEY(`id`),
	CONSTRAINT `exam_sessions_name_unique` UNIQUE(`name`)
);
--> statement-breakpoint
CREATE TABLE `exam_students` (
	`id` int AUTO_INCREMENT NOT NULL,
	`examId` int NOT NULL,
	`studentId` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `exam_students_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `teachers` (
	`id` int AUTO_INCREMENT NOT NULL,
	`username` varchar(50) NOT NULL,
	`password` varchar(255) NOT NULL,
	`name` varchar(100) NOT NULL,
	`email` varchar(320),
	`phone` varchar(20),
	`role` enum('admin','teacher_creator','teacher_grader') NOT NULL DEFAULT 'teacher_grader',
	`status` enum('active','inactive') NOT NULL DEFAULT 'active',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`lastLoginAt` timestamp,
	CONSTRAINT `teachers_id` PRIMARY KEY(`id`),
	CONSTRAINT `teachers_username_unique` UNIQUE(`username`)
);
--> statement-breakpoint
ALTER TABLE `exams` ADD `examSessionId` int NOT NULL;--> statement-breakpoint
ALTER TABLE `exams` ADD `creatorTeacherId` int NOT NULL;--> statement-breakpoint
ALTER TABLE `exams` ADD `graderTeacherId` int;--> statement-breakpoint
ALTER TABLE `report_cards` ADD `teacherComment` text;--> statement-breakpoint
CREATE INDEX `exam_student_idx` ON `exam_students` (`examId`,`studentId`);--> statement-breakpoint
CREATE INDEX `exam_session_idx` ON `exams` (`examSessionId`);--> statement-breakpoint
CREATE INDEX `creator_teacher_idx` ON `exams` (`creatorTeacherId`);--> statement-breakpoint
CREATE INDEX `grader_teacher_idx` ON `exams` (`graderTeacherId`);--> statement-breakpoint
ALTER TABLE `exam_templates` DROP COLUMN `semester`;--> statement-breakpoint
ALTER TABLE `exam_templates` DROP COLUMN `year`;