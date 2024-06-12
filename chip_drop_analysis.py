from pandas import read_csv
import settings

chip_df = read_csv(settings.chipfile, sep="\t").fillna('')
virus_df = read_csv(settings.virusfile, sep="\t").fillna('')
virus_df = virus_df[virus_df["Name"] != ""]

chip_drops = chip_df.merge(virus_df[["Name", "Drops1"]], left_on="Chip", right_on="Drops1", how="left")
chip_drops = chip_drops.merge(virus_df[["Name", "Drops2"]], left_on="Chip", right_on="Drops2", how="left")
chip_drops["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y'])
chip_df["Dropped By"] = chip_drops["Name_x"].combine_first(chip_drops['Name_y']).fillna('')

pass