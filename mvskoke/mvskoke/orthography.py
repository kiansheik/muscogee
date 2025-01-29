import csv, os, json

source_dir = os.path.dirname(os.path.abspath(__file__))
alt_ort_dir = os.path.join(source_dir, "alt_ort")

ALT_ORTS = dict()
nasais = "m n nh ng ã ẽ ĩ ỹ õ ũ mb nd".split(" ")
consoantes = "p b t s x k ' m n r nh ng mb nd ng g û î ŷ".split(" ")


def load_ort(ort):
    res = dict()
    with open(os.path.join(alt_ort_dir, f"{ort}.csv"), "r", encoding="utf-8") as f:
        # skip header of f, column 0 is the keys of the dict, column 1 the values of PHONEMIC_OT_FINBOW
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            res[row[0]] = row[1]
    ALT_ORTS[ort] = res


# search the folder alt_ort for all ort files, strip the .csv
def load_all_ort():
    for file in os.listdir(alt_ort_dir):
        if file.endswith(".csv"):
            load_ort(file[:-4])


with open(
    os.path.join(alt_ort_dir, "nasal_cluster_scores.json"), "r", encoding="utf-8"
) as f:
    help_score = json.load(f)

load_all_ort()

if __name__ == "__main__":
    print(ALT_ORTS)
