-- add new start letter field for indexing

ALTER TABLE `koncepts_koncept` add column `first_letter` varchar(1) NOT NULL;
