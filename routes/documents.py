from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import cloudinary
import cloudinary.uploader
from bson.objectid import ObjectId
from database import get_collection
from routes.auth import is_admin

bp = Blueprint("documents", __name__)


@bp.route("/documents", methods=["GET"])
def view_documents():
    if not is_admin():
        return redirect(url_for("auth.pass_manager"))

    documents = []
    doc_collection = get_collection("documents")
    if doc_collection is not None:
        try:
            documents = list(doc_collection.find().sort("_id", -1))
        except Exception as e:
            print(f"DB Error fetching documents: {e}")

    return render_template("documents.html", documents=documents)


@bp.route("/upload-doc", methods=["POST"])
def upload_document():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    try:
        result = cloudinary.uploader.upload(
            file,
            resource_type="auto",
            folder="portfolio_docs",
        )

        doc_collection = get_collection("documents")
        if doc_collection is not None:
            doc_collection.insert_one(
                {
                    "filename": file.filename,
                    "url": result["secure_url"],
                    "cloudinary_public_id": result["public_id"],
                    "resource_type": result.get("resource_type", "raw"),
                }
            )

        return jsonify({"message": "Uploaded successfully", "url": result["secure_url"]})
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500


@bp.route("/delete-doc/<doc_id>", methods=["POST"])
def delete_document(doc_id):
    if not is_admin():
        return redirect(url_for("auth.pass_manager"))

    doc_collection = get_collection("documents")
    if doc_collection is not None:
        try:
            doc = doc_collection.find_one({"_id": ObjectId(doc_id)})
            if doc:
                cloudinary.uploader.destroy(
                    doc["cloudinary_public_id"],
                    resource_type=doc.get("resource_type", "raw"),
                )
                doc_collection.delete_one({"_id": ObjectId(doc_id)})
        except Exception as e:
            print(f"Delete error: {e}")

    return redirect(url_for("documents.view_documents"))
