import pandas as pd
import numpy as np
import glob, os


def gather_csv(dir: str) -> pd.DataFrame:
    csv_files = glob.glob(os.path.join(dir, "*.csv"))
    # loop over the list of csv files
    df = pd.concat((pd.read_csv(f) for f in csv_files), ignore_index=True)
    df = df.rename(columns={"Unnamed: 0": "id"})
    df.drop_duplicates(subset=['id'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    to_remove = {
    r"&#039;": r"'",
    r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});": r" ",
    r"( ?(f|ht)(tp)(s?)(://)(\S*))": r"",
    r"(\s[:punct:]\s)": r"",
    r"(?<=[\?\!])[\?\!]+": r"",
    r"\d{9}": r"",
    r"(\s+)": r" ",
    r"^\s": r""
    }

    for pattern in to_remove.keys():
        df['comment'] = df['comment'].str.lower().str.replace(pattern, to_remove[pattern], regex=True)
    df = df[df['comment'].isna() == False]

    return df

def full_clean(dir: str) -> pd.DataFrame:
    return clean_text(gather_csv(dir))

