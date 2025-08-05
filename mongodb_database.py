
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import ast
from image_tools import search_and_download_image  # Your image search module

# os.environ['MONGODB_URI'] = os.getenv('MONGODB_URI')
class MongoDBDatabase:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection_schema(self, collection_name):
        sample_document = self.db[collection_name].find_one()
        return sample_document if sample_document else "No schema available"

    def run(self, collection_name, query):
        collection = self.db[collection_name]
        try:
            if query.startswith("collection.find"):
                code = query[len("collection.find("):-1]
                args = list(ast.literal_eval(f"[{code}]"))
                return list(collection.find(*args))

            elif query.startswith("collection.aggregate"):
                code = query[len("collection.aggregate("):-1]
                args = list(ast.literal_eval(f"[{code}]"))
                return list(collection.aggregate(*args))

            elif query.startswith("collection.updateOne"):
                code = query[len("collection.updateOne("):-1]
                args = list(ast.literal_eval(f"[{code}]"))

                filter_doc = args[0]
                update_doc = args[1]

                # Handle $push (adding new product)
                if "$push" in update_doc and "productDetails" in update_doc["$push"]:
                    product = update_doc["$push"]["productDetails"]

                    # Assign ObjectId if missing
                    if "_id" not in product:
                        product["_id"] = ObjectId()

                    # Convert warranty to datetime
                    if "warranty" in product and isinstance(product["warranty"], str):
                        try:
                            product["warranty"] = datetime.fromisoformat(product["warranty"])
                        except ValueError:
                            return [{"error": f"Invalid date format for warranty: {product['warranty']}"}]

                    # Search and assign image if missing or a prompt string
                    # if "product" in product and (not product.get("image") or isinstance(product["image"], str)):
                    #     image_name = search_and_download_image(product["image"] or product["product"])
                    #     product["image"] = image_name
                    # Search and assign image only if image key is missing or empty
                    if "product" in product:
                        image_name = search_and_download_image(product["product"])
                        product["image"] = image_name

                # Handle $set (updating productDetails)
                if "$set" in update_doc:
                    set_doc = update_doc["$set"]
                    for key, value in set_doc.items():
                        # Match keys like 'productDetails.$.image'
                        if key.startswith("productDetails") and key.endswith(".image"):
                            image_prompt = value
                            image_name = search_and_download_image(image_prompt)
                            update_doc["$set"][key] = image_name

                result = collection.update_one(filter_doc, update_doc)
                return [{"matched_count": result.matched_count, "modified_count": result.modified_count}]

            else:
                return [{"error": "Unsupported operation"}]

        except Exception as e:
            return [{"error": str(e)}]
