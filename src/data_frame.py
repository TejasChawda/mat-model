def get_levels(df):
    return df["Levels"].unique()


def get_scale_ids(df):
    return df["Scale_Id"].unique()


def get_max_level(levels):
    split_levels = [l.split(" ")[1] for l in levels]
    split_levels_int = [int(level) for level in split_levels]
    max_level = max(split_levels_int)

    return max_level
