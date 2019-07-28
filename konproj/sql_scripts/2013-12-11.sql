-- added unique name x koncepts constraint
-- Need to check for error in DB first!

ALTER TABLE `koncepts_koncept` ADD CONSTRAINT UNIQUE (`name`, `created_by_id`);