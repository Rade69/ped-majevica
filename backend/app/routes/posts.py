from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.post import Post
from app.schemas.post import PostSchema
from app.utils.responses import success_response, error_response, validation_error_response
import logging

logger = logging.getLogger(__name__)

# Database posts blueprint - for future admin CRUD operations
posts_bp = Blueprint("posts", __name__, url_prefix="/admin/posts")

# Inicijalizacija schema
post_schema = PostSchema()


@posts_bp.get("/")
@login_required
def list_posts():
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()

        return success_response(
            data={
                'posts': [
                    {
                        "id": post.id,
                        "title": post.title,
                        "published": post.published,
                        "created_at": post.created_at.isoformat(),
                    }
                    for post in posts
                ]
            },
            message=f"Pronađeno {len(posts)} postova"
        )
    except Exception as e:
        logger.error(f"Greška pri preuzimanju postova: {str(e)}", exc_info=True)
        return error_response(
            message="Greška pri preuzimanju postova",
            status_code=500
        )


@posts_bp.post("/")
@login_required
def create_post():
    try:
        data = request.get_json() or {}
        
        # Validacija inputa pomoću Marshmallow schema
        try:
            validated_data = post_schema.load(data)
        except Exception as e:
            if hasattr(e, 'messages'):
                # Marshmallow validation error
                return validation_error_response(e.messages)
            else:
                return error_response(f"Greška u validaciji: {str(e)}", status_code=400)
        
        # Kreiranje posta sa validiranim podacima
        post = Post(
            title=validated_data['title'],
            slug=validated_data.get('slug'),  # Slug je automatski generisan u schema
            content=validated_data['content'],
            preview=validated_data.get('preview'),
            category=validated_data.get('category', 'ostalo'),
            images=validated_data.get('images', []),
            published=validated_data.get('published', True),
        )
        
        # Postavljanje autora (trenutno ulogovani korisnik)
        post.author_id = current_user.id if current_user.is_authenticated else None

        db.session.add(post)
        db.session.commit()
        
        logger.info(f"Kreiran novi post: {post.title} (ID: {post.id})")

        return success_response(
            data={'post': {'id': post.id}},
            message="Post je uspešno kreiran",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri kreiranju posta: {str(e)}", exc_info=True)
        return error_response(
            message="Greška pri kreiranju posta",
            status_code=500
        )


@posts_bp.put("/<int:post_id>")
@login_required
def update_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        data = request.get_json() or {}
        
        # Validacija inputa (delimična - samo za polja koja se ažuriraju)
        try:
            validated_data = post_schema.load(data, partial=True)
        except Exception as e:
            if hasattr(e, 'messages'):
                return validation_error_response(e.messages)
            else:
                return error_response(f"Greška u validaciji: {str(e)}", status_code=400)
        
        # Ažuriranje polja samo ako su poslata u zahtevu
        if 'title' in validated_data:
            post.title = validated_data['title']
        if 'content' in validated_data:
            post.content = validated_data['content']
        if 'preview' in validated_data:
            post.preview = validated_data['preview']
        if 'category' in validated_data:
            post.category = validated_data['category']
        if 'images' in validated_data:
            post.images = validated_data['images']
        if 'published' in validated_data:
            post.published = validated_data['published']

        db.session.commit()
        
        logger.info(f"Ažuriran post: {post.title} (ID: {post.id})")

        return success_response(
            data={'post': {'id': post.id}},
            message="Post je uspešno ažuriran"
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri ažuriranju posta: {str(e)}", exc_info=True)
        return error_response(
            message="Greška pri ažuriranju posta",
            status_code=500
        )


@posts_bp.delete("/<int:post_id>")
@login_required
def delete_post(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        post_title = post.title  # Sačuvaj naslov za log
        
        db.session.delete(post)
        db.session.commit()
        
        logger.info(f"Obrisan post: {post_title} (ID: {post_id})")

        return success_response(
            message=f"Post '{post_title}' je uspešno obrisan"
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri brisanju posta: {str(e)}", exc_info=True)
        return error_response(
            message="Greška pri brisanju posta",
            status_code=500
        )
