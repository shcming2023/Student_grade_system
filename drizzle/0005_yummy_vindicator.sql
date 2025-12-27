ALTER TABLE `exam_templates` ADD `examSessionId` int NOT NULL;--> statement-breakpoint
CREATE INDEX `exam_session_idx` ON `exam_templates` (`examSessionId`);