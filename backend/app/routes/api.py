from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from app.extensions import db, limiter
from app.models.post import Post
from app.models.like import Like
from app.schemas.post import PostSchema
from app.utils.responses import success_response, error_response, validation_error_response
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Inicijalizacija schema
post_schema = PostSchema()


# DEBUG ENDPOINT - Check auth status
@api_bp.get('/debug/auth')
def debug_auth():
    """Debug endpoint to check authentication status"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.get_id() if current_user.is_authenticated else None,
        'username': current_user.username if current_user.is_authenticated else None,
        'session_keys': list(session.keys()),
        'cookies_received': list(request.cookies.keys())
    })


@api_bp.get('/posts')
@api_bp.get('/posts/')
def get_posts():
    """Get all blog posts from database"""
    try:
        # Query all published posts, ordered by creation date (newest first)
        posts = Post.query.filter_by(published=True).order_by(Post.created_at.desc()).all()

        # Convert to dict format matching JSON structure
        posts_list = [post.to_dict() for post in posts]

        return success_response(
            data={'posts': posts_list},
            message=f"Pronađeno {len(posts_list)} postova"
        )

    except Exception as e:
        logger.error(f"Greška pri preuzimanju postova: {str(e)}", exc_info=True)
        return error_response('Greška pri preuzimanju postova', status_code=500)


@api_bp.get('/posts/<int:post_id>')
@api_bp.get('/posts/<int:post_id>/')
def get_post(post_id):
    """Get single blog post by ID"""
    try:
        post = Post.query.get_or_404(post_id)
        return success_response(
            data=post.to_dict(),
            message="Post pronađen"
        )
    except Exception as e:
        logger.error(f"Greška pri preuzimanju posta {post_id}: {str(e)}")
        return error_response('Post nije pronađen', status_code=404)


@api_bp.get('/posts/slug/<slug>')
@api_bp.get('/posts/slug/<slug>/')
def get_post_by_slug(slug):
    """Get single blog post by slug"""
    try:
        post = Post.query.filter_by(slug=slug, published=True).first_or_404()
        return success_response(
            data=post.to_dict(),
            message="Post pronađen"
        )
    except Exception as e:
        logger.error(f"Greška pri preuzimanju posta po slug-u {slug}: {str(e)}")
        return error_response('Post nije pronađen', status_code=404)


# ========================================
# LIKE/UNLIKE ENDPOINTS
# ========================================

@api_bp.post('/posts/<int:post_id>/like')
@api_bp.post('/posts/<int:post_id>/like/')
@limiter.limit("10 per hour")  # Maksimalno 10 lajkova po satu
def like_post(post_id):
    """
    Like a post (no authentication required for MVP)
    Returns updated likes count
    """
    try:
        post = Post.query.get_or_404(post_id)

        # For MVP: Allow anonymous likes (track by session/IP later)
        # Increment likes count
        post.likes_count += 1
        db.session.commit()

        logger.info(f"Post {post_id} liked. New count: {post.likes_count}")

        return success_response(
            data={'likes_count': post.likes_count},
            message="Post lajkovan"
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri lajkovanju posta {post_id}: {str(e)}")
        return error_response("Greška pri lajkovanju posta", status_code=500)


@api_bp.delete('/posts/<int:post_id>/like')
@api_bp.delete('/posts/<int:post_id>/like/')
@limiter.limit("10 per hour")  # Maksimalno 10 unlajkova po satu
def unlike_post(post_id):
    """
    Unlike a post (no authentication required for MVP)
    Returns updated likes count
    """
    try:
        post = Post.query.get_or_404(post_id)

        # Decrement likes count (min 0)
        if post.likes_count > 0:
            post.likes_count -= 1
            db.session.commit()

        logger.info(f"Post {post_id} unliked. New count: {post.likes_count}")

        return success_response(
            data={'likes_count': post.likes_count},
            message="Post unlajkovan"
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri unlajkovanju posta {post_id}: {str(e)}")
        return error_response("Greška pri unlajkovanju posta", status_code=500)


@api_bp.get('/posts/<int:post_id>/likes')
@api_bp.get('/posts/<int:post_id>/likes/')
def get_post_likes(post_id):
    """Get likes count for a post"""
    try:
        post = Post.query.get_or_404(post_id)
        return success_response(
            data={
                'post_id': post_id,
                'likes_count': post.likes_count
            },
            message="Broj lajkova pronađen"
        )
    except Exception as e:
        logger.error(f"Greška pri preuzimanju lajkova za post {post_id}: {str(e)}")
        return error_response('Post nije pronađen', status_code=404)


# ========================================
# POST CREATE/UPDATE/DELETE ENDPOINTS
# ========================================

@api_bp.post('/posts')
@api_bp.post('/posts/')
@login_required
def create_post():
    """Create new blog post"""
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

        # Create new post with validated data
        # Support both content and content_markdown/content_html
        content = data.get('content_markdown', data.get('content_html', validated_data['content']))
        content_html = data.get('content_html')
        content_text = data.get('content_text')
        
        post = Post(
            title=validated_data['title'],
            slug=data.get('slug', validated_data['slug']),  # Use provided slug or auto-generated
            content=content,
            content_html=content_html,
            content_text=content_text,
            preview=data.get('preview', validated_data.get('preview')),
            category=data.get('category', validated_data.get('category', 'ostalo')),
            word_count=data.get('word_count', validated_data.get('word_count')),
            image_count=data.get('image_count', validated_data.get('image_count', 0)),
            images=data.get('images', validated_data.get('images', [])),
            author_id=current_user.id if current_user.is_authenticated else None,
            published=data.get('published', validated_data.get('published', True)),
        )

        # Ako je proslijeđen custom datum, koristi ga umjesto trenutnog
        if data.get('custom_date'):
            from datetime import datetime
            try:
                custom_datetime = datetime.fromisoformat(data.get('custom_date'))
                post.created_at = custom_datetime
            except ValueError:
                pass  # Ako format nije ispravan, koristi default

        db.session.add(post)
        db.session.commit()

        logger.info(f"Kreiran novi post: {post.title} (ID: {post.id})")

        return success_response(
            data={'id': post.id},
            message='Post kreiran uspješno',
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri kreiranju posta: {str(e)}", exc_info=True)
        return error_response('Greška pri kreiranju posta', status_code=500)


@api_bp.put('/posts/<int:post_id>')
@api_bp.put('/posts/<int:post_id>/')
@login_required
def update_post(post_id):
    """Update existing blog post"""
    logger.info(f"🔵 UPDATE POST {post_id}: User authenticated: {current_user.is_authenticated}")
    logger.info(f"🔵 UPDATE POST {post_id}: User ID: {current_user.get_id() if current_user.is_authenticated else 'None'}")
    try:
        post = Post.query.get_or_404(post_id)
        data = request.get_json()

        # Update fields
        post.title = data.get('title', post.title)
        post.slug = data.get('slug', post.slug)
        post.content = data.get('content_markdown', data.get('content_html', post.content))
        post.content_html = data.get('content_html', post.content_html)
        post.content_text = data.get('content_text', post.content_text)
        post.preview = data.get('preview', post.preview)
        post.category = data.get('category', post.category)
        post.word_count = data.get('word_count', post.word_count)
        post.image_count = data.get('image_count', post.image_count)
        post.images = data.get('images', post.images)
        post.published = data.get('published', post.published)

        # Ako je proslijeđen custom datum, ažuriraj created_at
        if data.get('custom_date'):
            from datetime import datetime
            try:
                custom_datetime = datetime.fromisoformat(data.get('custom_date'))
                post.created_at = custom_datetime
            except ValueError:
                pass  # Ako format nije ispravan, ne mijenjaj

        db.session.commit()

        logger.info(f"Ažuriran post: {post.title} (ID: {post.id})")

        return success_response(
            data={'id': post.id},
            message='Post ažuriran uspješno'
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri ažuriranju posta {post_id}: {str(e)}", exc_info=True)
        return error_response('Greška pri ažuriranju posta', status_code=500)


@api_bp.delete('/posts/<int:post_id>')
@api_bp.delete('/posts/<int:post_id>/')
@login_required
def delete_post(post_id):
    """Delete blog post"""
    try:
        post = Post.query.get_or_404(post_id)
        post_title = post.title  # Sačuvaj naslov za log
        
        db.session.delete(post)
        db.session.commit()

        logger.info(f"Obrisan post: {post_title} (ID: {post_id})")

        return success_response(
            message='Post obrisan uspješno'
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri brisanju posta {post_id}: {str(e)}", exc_info=True)
        return error_response('Greška pri brisanju posta', status_code=500)
