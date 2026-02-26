from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import cloudinary.uploader
from datetime import datetime
from bson.objectid import ObjectId
from config import Config
from database import get_collection, get_client
from routes.auth import is_admin

bp = Blueprint('documents', __name__)

# Configure Cloudinary
import cloudinary
cloudinary.config(
    cloud_name=Config.CLOUDINARY_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

@bp.route('/documents')
def documents_page():
    if not is_admin(): 
        return redirect(url_for('auth.view_logs')) 
    
    # Fetch existing docs from MongoDB
    docs = []
    if get_client() is not None:
        doc_collection = get_collection("document_logs")
        docs = list(doc_collection.find().sort("_id", -1))
    
    return render_template('documents.html', authenticated=True, documents=docs)

@bp.route('/upload-doc', methods=['POST'])
def upload_document():
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    file = request.files.get('file')
    if file:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(file, resource_type="auto")
        file_url = upload_result.get("secure_url")

        # Save record to MongoDB
        if get_client() is not None:
            doc_collection = get_collection("document_logs")
            doc_collection.insert_one({
                "filename": file.filename,
                "url": file_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify({"url": file_url}), 200
    
    return jsonify({"error": "Upload failed"}), 400

@bp.route('/delete-doc/<id>')
def delete_document(id):
    if not is_admin(): 
        return redirect(url_for('auth.view_logs'))
    
    if get_client() is not None:
        try:
            doc_collection = get_collection("document_logs")
            doc_collection.delete_one({"_id": ObjectId(id)})
        except Exception as e:
            print(f"Delete Error: {e}")
            
    return redirect(url_for('documents.documents_page'))
