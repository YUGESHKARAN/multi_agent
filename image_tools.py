# image_tools.py

import os
import requests
import boto3
import io
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

REGION = os.getenv("BUCKET_REGION")

# AWS S3 setup
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
    region_name=REGION,
)
BUCKET_NAME = os.getenv("BUCKET_NAME")

def search_and_download_image(query):
    print(f"Extracting product name from query and searching image: {query}")
    
    # Use only product name for image search
     # Use only product name for image search
    raw_product_name = query.strip().split("product name")[-1].split(",")[0].strip(" '")
    product_name = raw_product_name.replace(" ", "").lower()  # remove spaces and lowercase

    params = {
        "q": product_name,
        "tbm": "isch",
        "engine": "google",
        "ijn": "0",
        "api_key": os.getenv("SERP_API_KEY"),
    }

    res = requests.get("https://serpapi.com/search.json", params=params)
    data = res.json()

    if "images_results" not in data or not data["images_results"]:
        raise Exception("No image results found.")

    img_url = data["images_results"][0]["original"]
    img_data = requests.get(img_url).content

    filename = f"{quote_plus(product_name)}.jpg"

    # Upload to S3 directly from memory
    s3.upload_fileobj(io.BytesIO(img_data), BUCKET_NAME, filename)

    print(f"Image {filename} uploaded to S3 bucket {BUCKET_NAME}")
    return filename  # Store this in MongoDB
