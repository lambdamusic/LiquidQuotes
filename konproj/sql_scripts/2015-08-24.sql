
-- Adding new m2m fragments subjects


CREATE TABLE `koncepts_fragment_subjects` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `fragment_id` integer NOT NULL,
    `subject_id` integer NOT NULL,
    UNIQUE (`fragment_id`, `subject_id`)
)
;

ALTER TABLE `koncepts_fragment_subjects` ADD CONSTRAINT `fragment_id_refs_id_14ac9a76` FOREIGN KEY (`fragment_id`) REFERENCES `koncepts_fragment` (`id`);

ALTER TABLE `koncepts_fragment_subjects` ADD CONSTRAINT `subject_id_refs_id_59993d39` FOREIGN KEY (`subject_id`) REFERENCES `koncepts_subject` (`id`);


