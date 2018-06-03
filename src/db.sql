DROP TABLE IF EXISTS "article" CASCADE;
CREATE TABLE "article"(
  id serial primary key,
  created timestamp NOT NULL DEFAULT now(),
  updated timestamp NULL,
  title varchar(50),
  text text,
  category_id bigint not null
);

DROP TABLE IF EXISTS "category" CASCADE;
CREATE TABLE "category"(
  id serial primary key,
  created timestamp NOT NULL DEFAULT now(),
  updated timestamp NULL,
  title varchar(50)
);

DROP TABLE IF EXISTS "tag" CASCADE;
CREATE TABLE "tag"(
  id serial primary key,
  created timestamp NOT NULL DEFAULT now(),
  updated timestamp NULL,
  value varchar(50)
);

DROP TABLE IF EXISTS "article__tag" CASCADE;
CREATE TABLE "article__tag"(
  article_id bigint not null,
  tag_id bigint not null
);


ALTER TABLE "article" ADD CONSTRAINT "fk_article_category_id" FOREIGN KEY ("category_id") REFERENCES "category"("id");

ALTER TABLE "article__tag" ADD CONSTRAINT "fk_articletag_article_id" FOREIGN KEY ("article_id") REFERENCES "article"("id");

ALTER TABLE "article__tag" ADD CONSTRAINT "fk_articletag_tag_id" FOREIGN KEY ("tag_id") REFERENCES "tag"("id");
