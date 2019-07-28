-- add new fields for new folder/title structures

ALTER TABLE `koncepts_fragment` add column `title` varchar(250);
ALTER TABLE `koncepts_fragment` add column `comment` longtext;



-- revamp the Project model and link it via m2m relations



CREATE TABLE `koncepts_project_fragments` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `project_id` integer NOT NULL,
    `fragment_id` integer NOT NULL,
    UNIQUE (`project_id`, `fragment_id`)
)
;
ALTER TABLE `koncepts_project_fragments` ADD CONSTRAINT `fragment_id_refs_id_181c634d` FOREIGN KEY (`fragment_id`) REFERENCES `koncepts_fragment` (`id`);

CREATE TABLE `koncepts_project_koncepts` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `project_id` integer NOT NULL,
    `koncept_id` integer NOT NULL,
    UNIQUE (`project_id`, `koncept_id`)
)
;
ALTER TABLE `koncepts_project_koncepts` ADD CONSTRAINT `koncept_id_refs_id_175ce7fd` FOREIGN KEY (`koncept_id`) REFERENCES `koncepts_koncept` (`id`);


ALTER TABLE `koncepts_project_fragments` ADD CONSTRAINT `project_id_refs_id_134c9959` FOREIGN KEY (`project_id`) REFERENCES `koncepts_project` (`id`);
ALTER TABLE `koncepts_project_koncepts` ADD CONSTRAINT `project_id_refs_id_6aedd526` FOREIGN KEY (`project_id`) REFERENCES `koncepts_project` (`id`);