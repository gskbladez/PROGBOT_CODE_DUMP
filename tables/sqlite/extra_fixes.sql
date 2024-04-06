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

/* Simplify Virus Drops */

CREATE TABLE virus_drops AS SELECT virus, drop1, drop2 FROM virus, chip;

chip_drops = chip_df.merge(virus_df[["Name", "Drops1"]], left_on="Chip", right_on="Drops1", how="left")
chip_drops = chip_drops.merge(virus_df[["Name", "Drops2"]], left_on="Chip", right_on="Drops2", how="left")
chip_drops["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y'])
chip_df["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y']).fillna('')
