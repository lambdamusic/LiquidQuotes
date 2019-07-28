BEGIN;
CREATE TABLE `koncepts_relationkon` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `name` varchar(765) NOT NULL,
    `description` longtext NOT NULL
)
;
ALTER TABLE `koncepts_relationkon` ADD CONSTRAINT `created_by_id_refs_id_5f46cf7a` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_relationkon` ADD CONSTRAINT `updated_by_id_refs_id_5f46cf7a` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `koncepts_languages` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `name` varchar(765) NOT NULL,
    `description` longtext NOT NULL
)
;
ALTER TABLE `koncepts_languages` ADD CONSTRAINT `created_by_id_refs_id_72429009` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_languages` ADD CONSTRAINT `updated_by_id_refs_id_72429009` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `koncepts_faqitem` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `name` varchar(765) NOT NULL,
    `description` longtext NOT NULL,
    `orderno` integer,
    `category` varchar(3) NOT NULL
)
;
ALTER TABLE `koncepts_faqitem` ADD CONSTRAINT `created_by_id_refs_id_2d88a5f9` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_faqitem` ADD CONSTRAINT `updated_by_id_refs_id_2d88a5f9` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `koncepts_koncept` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `isprivate` bool NOT NULL,
    `name` varchar(250) NOT NULL,
    `name_url` varchar(250) NOT NULL,
    UNIQUE (`name`, `created_by_id`)
)
;
ALTER TABLE `koncepts_koncept` ADD CONSTRAINT `created_by_id_refs_id_2435a082` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_koncept` ADD CONSTRAINT `updated_by_id_refs_id_2435a082` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `koncepts_fragment` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `isprivate` bool NOT NULL,
    `text` longtext,
    `source_id` integer,
    `ismine` bool NOT NULL,
    `isdictionary` bool NOT NULL,
    `isbookmark` bool NOT NULL,
    `language_id` integer,
    `location` varchar(100) NOT NULL,
    `name_url` varchar(250) NOT NULL
)
;
ALTER TABLE `koncepts_fragment` ADD CONSTRAINT `created_by_id_refs_id_6d5ee495` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_fragment` ADD CONSTRAINT `updated_by_id_refs_id_6d5ee495` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_fragment` ADD CONSTRAINT `language_id_refs_id_5f5269af` FOREIGN KEY (`language_id`) REFERENCES `koncepts_languages` (`id`);
CREATE TABLE `koncepts_document` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `isprivate` bool NOT NULL,
    `title` varchar(300) NOT NULL,
    `author` varchar(200) NOT NULL,
    `pubyear` integer,
    `url` varchar(300) NOT NULL,
    `description` longtext NOT NULL,
    `fulltext` longtext NOT NULL,
    `name_url` varchar(250) NOT NULL,
    `searchindex` longtext NOT NULL
)
;
ALTER TABLE `koncepts_document` ADD CONSTRAINT `created_by_id_refs_id_39076398` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_document` ADD CONSTRAINT `updated_by_id_refs_id_39076398` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_fragment` ADD CONSTRAINT `source_id_refs_id_2349b1b0` FOREIGN KEY (`source_id`) REFERENCES `koncepts_document` (`id`);
CREATE TABLE `koncepts_project` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `isprivate` bool NOT NULL,
    `name` varchar(200) NOT NULL,
    `description` longtext NOT NULL,
    `name_url` varchar(250) NOT NULL
)
;
ALTER TABLE `koncepts_project` ADD CONSTRAINT `created_by_id_refs_id_5a30ec41` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_project` ADD CONSTRAINT `updated_by_id_refs_id_5a30ec41` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `koncepts_tag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `name` varchar(765) NOT NULL,
    `description` longtext NOT NULL,
    `name_url` varchar(250) NOT NULL,
    `totcount` integer
)
;
ALTER TABLE `koncepts_tag` ADD CONSTRAINT `created_by_id_refs_id_4cc3aae` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_tag` ADD CONSTRAINT `updated_by_id_refs_id_4cc3aae` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `koncepts_intfrag_tags` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `intfrag_id` integer NOT NULL,
    `tag_id` integer NOT NULL,
    UNIQUE (`intfrag_id`, `tag_id`)
)
;
ALTER TABLE `koncepts_intfrag_tags` ADD CONSTRAINT `tag_id_refs_id_48806933` FOREIGN KEY (`tag_id`) REFERENCES `koncepts_tag` (`id`);
CREATE TABLE `koncepts_intfrag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `isprivate` bool NOT NULL,
    `koncept_id` integer NOT NULL,
    `fragment_id` integer NOT NULL,
    `project_id` integer,
    `orderno` integer
)
;
ALTER TABLE `koncepts_intfrag` ADD CONSTRAINT `created_by_id_refs_id_6814930d` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_intfrag` ADD CONSTRAINT `updated_by_id_refs_id_6814930d` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_intfrag` ADD CONSTRAINT `project_id_refs_id_260a7fb9` FOREIGN KEY (`project_id`) REFERENCES `koncepts_project` (`id`);
ALTER TABLE `koncepts_intfrag` ADD CONSTRAINT `koncept_id_refs_id_5c3ae230` FOREIGN KEY (`koncept_id`) REFERENCES `koncepts_koncept` (`id`);
ALTER TABLE `koncepts_intfrag` ADD CONSTRAINT `fragment_id_refs_id_76d55ad` FOREIGN KEY (`fragment_id`) REFERENCES `koncepts_fragment` (`id`);
ALTER TABLE `koncepts_intfrag_tags` ADD CONSTRAINT `intfrag_id_refs_id_57079326` FOREIGN KEY (`intfrag_id`) REFERENCES `koncepts_intfrag` (`id`);
CREATE TABLE `koncepts_intkon` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created_at` datetime NOT NULL,
    `updated_at` datetime NOT NULL,
    `editedrecord` bool NOT NULL,
    `review` bool NOT NULL,
    `internal_notes` longtext NOT NULL,
    `created_by_id` integer,
    `updated_by_id` integer,
    `isprivate` bool NOT NULL,
    `term1_id` integer NOT NULL,
    `term2_id` integer NOT NULL,
    `description` longtext NOT NULL,
    `relation_id` integer,
    `hasPart` bool NOT NULL,
    `project_id` integer,
    `orderno` integer
)
;
ALTER TABLE `koncepts_intkon` ADD CONSTRAINT `created_by_id_refs_id_37d8fce0` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_intkon` ADD CONSTRAINT `updated_by_id_refs_id_37d8fce0` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `koncepts_intkon` ADD CONSTRAINT `term1_id_refs_id_66d5dd1d` FOREIGN KEY (`term1_id`) REFERENCES `koncepts_koncept` (`id`);
ALTER TABLE `koncepts_intkon` ADD CONSTRAINT `term2_id_refs_id_66d5dd1d` FOREIGN KEY (`term2_id`) REFERENCES `koncepts_koncept` (`id`);
ALTER TABLE `koncepts_intkon` ADD CONSTRAINT `relation_id_refs_id_36e7680b` FOREIGN KEY (`relation_id`) REFERENCES `koncepts_relationkon` (`id`);
ALTER TABLE `koncepts_intkon` ADD CONSTRAINT `project_id_refs_id_15527334` FOREIGN KEY (`project_id`) REFERENCES `koncepts_project` (`id`);
COMMIT;
