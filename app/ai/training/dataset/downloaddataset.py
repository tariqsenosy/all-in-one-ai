import os
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()



datasets = {
   # "accident": "pedduhemasri/accident-images",
    #"fire":     "phylake1337/fire-dataset",
    #"garbage":  "asdasdasasdas/garbage-classification",
    #"violence": "abdulmananraja/real-life-violence-situations",
  #  "other":    "techsash/waste-classification-data"
}



BASE = "training/dataset"
os.makedirs(BASE, exist_ok=True)



for category, dataset_name in datasets.items():
    print(f"\n⬇ Downloading {category} ...")
    target = os.path.join(BASE, category)
    os.makedirs(target, exist_ok=True)
    api.dataset_download_files(dataset_name, path=target, unzip=True)
    print(f"✔ Done {category}")

print("\n🎉 All datasets downloaded successfully!")
