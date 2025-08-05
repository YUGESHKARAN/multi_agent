
import os
import requests
import boto3
import io
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

REGION = os.getenv("BUCKET_REGION")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# AWS S3 setup
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
    region_name=REGION,
)
BUCKET_NAME = os.getenv("BUCKET_NAME")

def search_and_download_image(query):
    print(f"Searching Unsplash for image : {query}")
    
    # Use only product name for image search
     # Use only product name for image search
    # raw_product_name = query.strip().split("product name")[-1].split(",")[0].strip(" ")
    product_name = query.strip().lower().replace(" ", "+")

    response = requests.get(
        "https://api.unsplash.com/search/photos",
        params={
            "query": product_name,
            "per_page": 1,
            "orientation": "squarish",
            "client_id": UNSPLASH_ACCESS_KEY,
        },
    )
    data = response.json()

    if "results" not in data or not data["results"]:
        raise Exception(f"No Unsplash image results found for: {query}")

    img_url = data["results"][0]["urls"]["regular"]
    img_data = requests.get(img_url).content

    filename = f"{quote_plus(query.strip().lower())}.jpg"

    # Upload to S3
    s3.upload_fileobj(io.BytesIO(img_data), BUCKET_NAME, filename)

    print(f"Image '{filename}' uploaded to S3 bucket '{BUCKET_NAME}'")
    return filename  # Store this in MongoDB