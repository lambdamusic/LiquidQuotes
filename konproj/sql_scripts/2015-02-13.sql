-- add new fields for fragment orderno within source

ALTER TABLE `koncepts_fragment` add column `orderno` integer;


-- add new fields for fragment tags

CREATE TABLE `koncepts_fragment_tags` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `fragment_id` integer NOT NULL,
    `tag_id` integer NOT NULL,
    UNIQUE (`fragment_id`, `tag_id`)
)
;

ALTER TABLE `koncepts_fragment_tags` ADD CONSTRAINT `tag_id_refs_id_491985b` FOREIGN KEY (`tag_id`) REFERENCES `koncepts_tag` (`id`);
ALTER TABLE `koncepts_fragment_tags` ADD CONSTRAINT `fragment_id_refs_id_39568eee` FOREIGN KEY (`fragment_id`) REFERENCES `koncepts_fragment` (`id`);


-- add new desc field to koncept [2015-03-16]

ALTER TABLE `koncepts_koncept` add column `description` longtext NOT NULL;





