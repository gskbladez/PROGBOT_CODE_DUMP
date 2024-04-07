/* Create Chip Tags */
CREATE TEMP TABLE chip_tag_strings AS SELECT DISTINCT tags FROM chip WHERE tags != '';
UPDATE chip_tag_strings SET tags = REPLACE(tags, ', ', '", "');
UPDATE chip_tag_strings SET tags = '["' || tags || '"]';
CREATE TABLE chip_tags AS SELECT DISTINCT trim(lower(json_each.value)) AS tag FROM chip_tag_strings, json_each(tags);
DROP TABLE chip_tag_strings;

/* Create Virus Tags */
CREATE TEMP TABLE virus_tag_strings AS SELECT DISTINCT tags FROM virus WHERE tags != '';
UPDATE virus_tag_strings SET tags = REPLACE(tags, '; ', '", "');
UPDATE virus_tag_strings SET tags = '["' || tags || '"]';
CREATE TABLE virus_tags AS SELECT DISTINCT trim(lower(json_each.value)) AS tag FROM virus_tag_strings, json_each(tags) WHERE tag != 'none';
DROP TABLE virus_tag_strings;

/* Improve compatability with sqlite3 */
ALTER TABLE chip RENAME COLUMN 'From?' TO 'Source';
ALTER TABLE playermade_chip RENAME COLUMN 'From?' TO 'Source';

/* Simplify Virus Drops */

CREATE TABLE virus_drops AS SELECT virus, drop1, drop2 FROM virus, chip;

/* Add Chip Tag Count */
ALTER TABLE chip_tags ADD COLUMN Count INT;
update chip_tags set count = (select count(1) as Count from chip where tags like '%' || tag || '%');

/* Add Chip Categories */
CREATE TABLE chip_category AS SELECT DISTINCT Category FROM Chip WHERE Category != '';
ALTER TABLE chip_category ADD COLUMN Count INT;
update chip_category set count = (select count(1) as Count from chip where chip.category=chip_category.category);


/* chip_drops = chip_df.merge(virus_df[["Name", "Drops1"]], left_on="Chip", right_on="Drops1", how="left")
chip_drops = chip_drops.merge(virus_df[["Name", "Drops2"]], left_on="Chip", right_on="Drops2", how="left")
chip_drops["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y'])
chip_df["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y']).fillna('') */

CREATE TABLE alias (Item, Alias, Source);

/* Create Chip Aliases */
CREATE TEMP TABLE chip_alias_strings AS SELECT DISTINCT Chip, alias FROM chip WHERE alias != '';
UPDATE chip_alias_strings SET alias = REPLACE(alias, ',', '", "');
UPDATE chip_alias_strings SET alias = '["' || alias || '"]';
INSERT INTO Alias SELECT Chip, trim(json_each.value) as alias, 'Chip' FROM chip_alias_strings, json_each(alias);
DROP TABLE chip_alias_strings;