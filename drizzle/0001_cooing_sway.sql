CREATE TABLE `classes` (
	`id` int AUTO_INCREMENT NOT NULL,
	`gradeId` int NOT NULL,
	`name` varchar(100) NOT NULL,
	`fullName` varchar(200) NOT NULL,
	`teacherId` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `classes_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `exam_templates` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(200) NOT NULL,
	`subjectId` int NOT NULL,
	`gradeId` int NOT NULL,
	`totalScore` decimal(5,1) NOT NULL,
	`semester` varchar(50),
	`year` int,
	`description` text,
	`createdBy` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `exam_templates_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `exams` (
	`id` int AUTO_INCREMENT NOT NULL,
	`examTemplateId` int NOT NULL,
	`classId` int NOT NULL,
	`examDate` timestamp NOT NULL,
	`name` varchar(200) NOT NULL,
	`status` enum('draft','published','completed') NOT NULL DEFAULT 'draft',
	`createdBy` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `exams_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `grades` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(50) NOT NULL,
	`displayName` varchar(100) NOT NULL,
	`sortOrder` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `grades_id` PRIMARY KEY(`id`),
	CONSTRAINT `grades_name_unique` UNIQUE(`name`)
);
--> statement-breakpoint
CREATE TABLE `questions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`examTemplateId` int NOT NULL,
	`questionNumber` int NOT NULL,
	`module` varchar(100),
	`knowledgePoint` text,
	`questionType` varchar(100),
	`score` decimal(5,1) NOT NULL,
	`sortOrder` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `questions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `report_cards` (
	`id` int AUTO_INCREMENT NOT NULL,
	`examId` int NOT NULL,
	`studentId` int NOT NULL,
	`totalScore` decimal(6,2) NOT NULL,
	`percentage` decimal(5,2),
	`classRank` int,
	`gradeRank` int,
	`analysis` text,
	`suggestions` text,
	`weakPoints` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `report_cards_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `scores` (
	`id` int AUTO_INCREMENT NOT NULL,
	`examId` int NOT NULL,
	`studentId` int NOT NULL,
	`questionId` int NOT NULL,
	`score` decimal(5,1) NOT NULL,
	`createdBy` int NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `scores_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `students` (
	`id` int AUTO_INCREMENT NOT NULL,
	`studentNumber` varchar(50) NOT NULL,
	`name` varchar(100) NOT NULL,
	`classId` int NOT NULL,
	`gender` enum('male','female'),
	`dateOfBirth` timestamp,
	`parentContact` varchar(100),
	`status` enum('active','inactive') NOT NULL DEFAULT 'active',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `students_id` PRIMARY KEY(`id`),
	CONSTRAINT `students_studentNumber_unique` UNIQUE(`studentNumber`)
);
--> statement-breakpoint
CREATE TABLE `subjects` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(100) NOT NULL,
	`code` varchar(50) NOT NULL,
	`category` varchar(50) NOT NULL,
	`description` text,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `subjects_id` PRIMARY KEY(`id`),
	CONSTRAINT `subjects_name_unique` UNIQUE(`name`),
	CONSTRAINT `subjects_code_unique` UNIQUE(`code`)
);
--> statement-breakpoint
CREATE INDEX `grade_idx` ON `classes` (`gradeId`);--> statement-breakpoint
CREATE INDEX `subject_grade_idx` ON `exam_templates` (`subjectId`,`gradeId`);--> statement-breakpoint
CREATE INDEX `class_idx` ON `exams` (`classId`);--> statement-breakpoint
CREATE INDEX `exam_template_idx` ON `exams` (`examTemplateId`);--> statement-breakpoint
CREATE INDEX `exam_template_idx` ON `questions` (`examTemplateId`);--> statement-breakpoint
CREATE INDEX `exam_student_idx` ON `report_cards` (`examId`,`studentId`);--> statement-breakpoint
CREATE INDEX `exam_student_idx` ON `scores` (`examId`,`studentId`);--> statement-breakpoint
CREATE INDEX `question_idx` ON `scores` (`questionId`);--> statement-breakpoint
CREATE INDEX `class_idx` ON `students` (`classId`);