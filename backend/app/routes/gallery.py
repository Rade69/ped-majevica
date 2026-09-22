from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required
from app.extensions import db
from app.models.gallery import GalleryImage
from app.utils.responses import success_response, error_response, validation_error_response
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
from io import BytesIO
from PIL import Image

gallery_bp = Blueprint('gallery', __name__, url_prefix='/api/gallery')

# Konfiguracija
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
THUMBNAIL_SIZE = (300, 300)  # Veličina thumbnail-a

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(image_data, mime_type):
    """Kreira thumbnail od slike"""
    try:
        img = Image.open(BytesIO(image_data))
        img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        
        thumb_io = BytesIO()
        img.save(thumb_io, format=img.format or 'JPEG', quality=85)
        thumb_io.seek(0)
        
        return thumb_io.getvalue(), mime_type
    except Exception as e:
        current_app.logger.error(f"Greška pri kreiranju thumbnail-a: {e}")
        return None, None

def get_image_dimensions(image_data):
    """Dobija dimenzije slike"""
    try:
        img = Image.open(BytesIO(image_data))
        return img.width, img.height
    except:
        return None, None


@gallery_bp.get('/')
def get_gallery():
    """Dohvati sve slike iz galerije (bez binary podataka)"""
    try:
        category = request.args.get('category')
        published_only = request.args.get('published', 'true').lower() == 'true'
        
        query = GalleryImage.query
        
        if category:
            query = query.filter_by(category=category)
        
        if published_only:
            query = query.filter_by(published=True)
        
        # Sortiraj po order pa po datumu
        images = query.order_by(GalleryImage.order.asc(), GalleryImage.created_at.desc()).all()
        
        return success_response(
            data={'images': [img.to_dict() for img in images]},
            message=f"Pronađeno {len(images)} slika"
        )
        
    except Exception as e:
        return error_response(f"Greška pri preuzimanju galerije: {str(e)}", status_code=500)


@gallery_bp.get('/<int:image_id>')
def get_image(image_id):
    """Dohvati jednu sliku (bez binary podataka)"""
    try:
        image = GalleryImage.query.get_or_404(image_id)
        return success_response(data=image.to_dict())
    except Exception as e:
        return error_response("Slika nije pronađena", status_code=404)


@gallery_bp.get('/<int:image_id>/image')
def serve_image(image_id):
    """Servira binary podatak slike"""
    try:
        image = GalleryImage.query.get_or_404(image_id)
        
        # Kreiraj BytesIO od binary podataka
        img_io = BytesIO(image.image_data)
        
        # Proveri MIME tip
        mimetype = image.image_mime
        if not mimetype or mimetype not in ['image/jpeg', 'image/png', 'image/webp', 'image/gif']:
            mimetype = 'image/jpeg'
        
        return send_file(
            img_io,
            mimetype=mimetype,
            as_attachment=False
        )
    except HTTPException:
        raise
    except Exception as e:
        current_app.logger.error(f"Greška pri serviranju slike {image_id}: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return error_response("Greška pri serviranju slike: " + str(e), status_code=500)


@gallery_bp.get('/<int:image_id>/thumbnail')
def serve_thumbnail(image_id):
    """Servira thumbnail slike"""
    try:
        image = GalleryImage.query.get_or_404(image_id)
        
        # Ako postoji thumbnail, koristi ga
        if image.thumbnail_data:
            img_io = BytesIO(image.thumbnail_data)
            return send_file(
                img_io,
                mimetype=image.thumbnail_mime or image.image_mime,
                as_attachment=False
            )
        
        # Inače vrati originalnu sliku
        return serve_image(image_id)
        
    except HTTPException:
        raise
    except Exception as e:
        current_app.logger.error(f"Greška pri serviranju thumbnail-a: {e}")
        # Fallback na originalnu sliku
        return serve_image(image_id)


@gallery_bp.post('/')
@login_required
def create_image():
    """Dodaj novu sliku u galeriju (čuvanje u bazi)"""
    try:
        # Proveri da li postoji fajl u zahtevu
        if 'file' not in request.files:
            return error_response("Fajl nije pronađen u zahtevu", status_code=400)
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response("Fajl nije izabran", status_code=400)
        
        if not allowed_file(file.filename):
            return error_response("Nedozvoljen tip fajla. Dozvoljeni formati: PNG, JPG, JPEG, WEBP, GIF", status_code=400)
        
        # Pročitaj binary podatak
        image_data = file.read()
        image_size = len(image_data)
        
        # Proveri veličinu
        if image_size > MAX_FILE_SIZE:
            return error_response(f"Fajl je prevelik. Maksimalna veličina: {MAX_FILE_SIZE // 1024 // 1024}MB", status_code=400)
        
        # Odredi MIME tip
        ext = file.filename.rsplit('.', 1)[1].lower()
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        image_mime = mime_types.get(ext, 'image/jpeg')
        
        # Dobavi dimenzije
        width, height = get_image_dimensions(image_data)
        
        # Kreiraj thumbnail
        thumbnail_data, thumbnail_mime = create_thumbnail(image_data, image_mime)
        
        # Dobavi metadata iz form-e
        title = request.form.get('title', 'Bez naslova')
        description = request.form.get('description', '')
        category = request.form.get('category', 'ostalo')
        tags = request.form.get('tags', '')
        order = int(request.form.get('order', 0))
        published = request.form.get('published', 'true').lower() == 'true'
        
        # Kreiraj zapis u bazi
        image = GalleryImage(
            title=title,
            description=description,
            image_data=image_data,
            image_mime=image_mime,
            image_size=image_size,
            image_width=width,
            image_height=height,
            thumbnail_data=thumbnail_data,
            thumbnail_mime=thumbnail_mime,
            category=category,
            tags=tags,
            order=order,
            published=published
        )
        
        db.session.add(image)
        db.session.commit()
        
        return success_response(
            data={'image': image.to_dict()},
            message="Slika je uspešno dodata u galeriju",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Greška pri dodavanju slike: {str(e)}", status_code=500)


@gallery_bp.put('/<int:image_id>')
@login_required
def update_image(image_id):
    """Izmeni podatke o slici (ne i binary)"""
    try:
        image = GalleryImage.query.get_or_404(image_id)
        
        # Update fields from form data
        data = request.form
        
        if 'title' in data:
            image.title = data['title']
        if 'description' in data:
            image.description = data['description']
        if 'category' in data:
            image.category = data['category']
        if 'tags' in data:
            image.tags = data['tags']
        if 'order' in data:
            image.order = int(data['order'])
        if 'published' in data:
            image.published = data['published'].lower() == 'true'
        
        # Ako je poslat NOVI fajl, zameni stari
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and allowed_file(file.filename):
                # Obriši stare binary podatke
                image.image_data = None
                image.thumbnail_data = None
                
                # Pročitaj novi fajl
                image_data = file.read()
                image_size = len(image_data)
                
                ext = file.filename.rsplit('.', 1)[1].lower()
                mime_types = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'webp': 'image/webp',
                    'gif': 'image/gif'
                }
                image_mime = mime_types.get(ext, 'image/jpeg')
                
                width, height = get_image_dimensions(image_data)
                thumbnail_data, thumbnail_mime = create_thumbnail(image_data, image_mime)
                
                image.image_data = image_data
                image.image_mime = image_mime
                image.image_size = image_size
                image.image_width = width
                image.image_height = height
                image.thumbnail_data = thumbnail_data
                image.thumbnail_mime = thumbnail_mime
        
        db.session.commit()
        
        return success_response(
            data={'image': image.to_dict()},
            message="Slika je uspešno ažurirana"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Greška pri ažuriranju slike: {str(e)}", status_code=500)


@gallery_bp.delete('/<int:image_id>')
@login_required
def delete_image(image_id):
    """Obriši sliku iz galerije"""
    try:
        image = GalleryImage.query.get_or_404(image_id)
        
        # Obriši zapis iz baze (binary će biti obrisan automatski)
        db.session.delete(image)
        db.session.commit()
        
        return success_response(message="Slika je uspešno obrisana")
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Greška pri brisanju slike: {str(e)}", status_code=500)


@gallery_bp.get('/categories')
def get_categories():
    """Dohvati sve kategorije koje se koriste u galeriji"""
    try:
        categories = db.session.query(GalleryImage.category).distinct().all()
        categories_list = [cat[0] for cat in categories if cat[0]]
        
        return success_response(
            data={'categories': categories_list},
            message=f"Pronađeno {len(categories_list)} kategorija"
        )
    except Exception as e:
        return error_response(f"Greška pri preuzimanju kategorija: {str(e)}", status_code=500)
