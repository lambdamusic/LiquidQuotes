-- add new search index field for documents

ALTER TABLE `koncepts_document` add column `searchindex` longtext NOT NULL;

