from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from app.extensions import db, limiter
from app.models.post import Post
from app.models.like import Like
from app.schemas.post import PostSchema
from app.utils.responses import (
    success_response,
    error_response,
    validation_error_response,
)
from app.utils.decorators import role_required, editor_required
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Inicijalizacija schema
post_schema = PostSchema()


# ========================================
# CSRF TOKEN ENDPOINT
# ========================================


@api_bp.get("/csrf-token")
@api_bp.get("/csrf-token/")
def get_csrf_token():
    """Return CSRF token for frontend forms"""
    return jsonify({"csrf_token": generate_csrf()})


# DEBUG ENDPOINT - Check auth status (PROTECTED)
@api_bp.get("/debug/auth")
def debug_auth():
    """Debug endpoint to check authentication status.
    Requires authentication in development, blocked in production.
    """
    from flask import current_app

    # Block in production
    if current_app.config.get("FLASK_ENV") == "production":
        return jsonify({"error": "Debug endpoints disabled in production"}), 403

    # Require authentication in development
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required for debug endpoints"}), 401

    return jsonify(
        {
            "authenticated": current_user.is_authenticated,
            "user_id": current_user.get_id() if current_user.is_authenticated else None,
            "username": (
                current_user.username if current_user.is_authenticated else None
            ),
            "session_keys": list(session.keys()),
            "cookies_received": list(request.cookies.keys()),
        }
    )


@api_bp.get("/posts")
@api_bp.get("/posts/")
def get_posts():
    """Get all blog posts with pagination"""
    try:
        # Pagination params
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)
        category = request.args.get("category", None)
        search = request.args.get("search", None)

        # Query
        query = Post.query.filter_by(published=True)
        if category:
            query = query.filter_by(category=category)
        if search:
            # Search in title and content_text (case-insensitive)
            from sqlalchemy import or_
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Post.title.ilike(search_term),
                    Post.content_text.ilike(search_term),
                    Post.preview.ilike(search_term)
                )
            )

        query = query.order_by(Post.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        posts_list = [post.to_dict() for post in pagination.items]

        response_data = {
            "posts": posts_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
                "next_page": page + 1 if pagination.has_next else None,
                "prev_page": page - 1 if pagination.has_prev else None,
            },
        }

        return success_response(
            data=response_data,
            message=f"Pronađeno {pagination.total} postova, stranica {page}",
        )

    except Exception as e:
        logger.error(f"Greška pri preuzimanju postova: {str(e)}", exc_info=True)
        return error_response("Greška pri preuzimanju postova", status_code=500)


@api_bp.get("/posts/<int:post_id>")
@api_bp.get("/posts/<int:post_id>/")
def get_post(post_id):
    """Get single blog post by ID"""
    try:
        post = Post.query.get_or_404(post_id)
        return success_response(data=post.to_dict(), message="Post pronađen")
    except Exception as e:
        logger.error(f"Greška pri preuzimanju posta {post_id}: {str(e)}")
        return error_response("Post nije pronađen", status_code=404)


@api_bp.get("/posts/slug/<slug>")
@api_bp.get("/posts/slug/<slug>/")
def get_post_by_slug(slug):
    """Get single blog post by slug"""
    try:
        post = Post.query.filter_by(slug=slug, published=True).first_or_404()
        return success_response(data=post.to_dict(), message="Post pronađen")
    except Exception as e:
        logger.error(f"Greška pri preuzimanju posta po slug-u {slug}: {str(e)}")
        return error_response("Post nije pronađen", status_code=404)


# ========================================
# LIKE/UNLIKE ENDPOINTS - WITH AUTH
# ========================================


@api_bp.post("/posts/<int:post_id>/like")
@api_bp.post("/posts/<int:post_id>/like/")
@limiter.limit("20 per hour")  # Maksimalno 20 lajkova po satu po korisniku
@login_required  # AUTENTIFIKACIJA OBavezna!
def like_post(post_id):
    """
    Like a post - requires authentication
    Returns updated likes count and whether user has liked
    """
    try:
        post = Post.query.get_or_404(post_id)

        # Proveri da li korisnik već lajkovao
        existing_like = Like.query.filter_by(
            user_id=current_user.id, post_id=post_id
        ).first()

        if existing_like:
            return success_response(
                data={
                    "likes_count": post.likes_count,
                    "user_has_liked": True,
                    "message": "Već ste lajkovali ovaj post",
                },
                message="Već ste lajkovali ovaj post",
            )

        # Kreiraj novi like
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)

        # Inkrementiraj likes count
        post.likes_count += 1
        db.session.commit()

        logger.info(
            f"✅ Post {post_id} liked by user {current_user.id}. New count: {post.likes_count}"
        )

        return success_response(
            data={"likes_count": post.likes_count, "user_has_liked": True},
            message="Post lajkovan",
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri lajkovanju posta {post_id}: {str(e)}")
        return error_response("Greška pri lajkovanju posta", status_code=500)


@api_bp.delete("/posts/<int:post_id>/like")
@api_bp.delete("/posts/<int:post_id>/like/")
@limiter.limit("20 per hour")  # Maksimalno 20 unlajkova po satu
@login_required  # AUTENTIFIKACIJA OBavezna!
def unlike_post(post_id):
    """
    Unlike a post - requires authentication
    Returns updated likes count
    """
    try:
        post = Post.query.get_or_404(post_id)

        # Pronađi like
        existing_like = Like.query.filter_by(
            user_id=current_user.id, post_id=post_id
        ).first()

        if not existing_like:
            return success_response(
                data={
                    "likes_count": post.likes_count,
                    "user_has_liked": False,
                    "message": "Niste lajkovali ovaj post",
                },
                message="Niste lajkovali ovaj post",
            )

        # Obriši like
        db.session.delete(existing_like)

        # Dekrementiraj likes count (min 0)
        if post.likes_count > 0:
            post.likes_count -= 1

        db.session.commit()

        logger.info(
            f"✅ Post {post_id} unliked by user {current_user.id}. New count: {post.likes_count}"
        )

        return success_response(
            data={"likes_count": post.likes_count, "user_has_liked": False},
            message="Post unlajkovan",
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri unlajkovanju posta {post_id}: {str(e)}")
        return error_response("Greška pri unlajkovanju posta", status_code=500)


@api_bp.get("/posts/<int:post_id>/likes")
@api_bp.get("/posts/<int:post_id>/likes/")
def get_post_likes(post_id):
    """Get likes count for a post and whether current user has liked"""
    try:
        post = Post.query.get_or_404(post_id)

        # Proveri da li je trenutni korisnik lajkovao
        user_has_liked = False
        if current_user.is_authenticated:
            existing_like = Like.query.filter_by(
                user_id=current_user.id, post_id=post_id
            ).first()
            user_has_liked = existing_like is not None

        return success_response(
            data={
                "post_id": post_id,
                "likes_count": post.likes_count,
                "user_has_liked": user_has_liked,
            },
            message="Broj lajkova pronađen",
        )
    except Exception as e:
        logger.error(f"Greška pri preuzimanju lajkova za post {post_id}: {str(e)}")
        return error_response("Post nije pronađen", status_code=404)


# ========================================
# POST CREATE/UPDATE/DELETE ENDPOINTS
# ========================================


@api_bp.post("/posts")
@api_bp.post("/posts/")
@login_required
def create_post():
    """Create new blog post"""
    try:
        data = request.get_json() or {}

        # Validacija inputa pomoću Marshmallow schema
        try:
            validated_data = post_schema.load(data)
        except Exception as e:
            if hasattr(e, "messages"):
                # Marshmallow validation error
                return validation_error_response(e.messages)
            else:
                return error_response(f"Greška u validaciji: {str(e)}", status_code=400)

        # Create new post with validated data
        # Support both content and content_markdown/content_html
        content = data.get(
            "content_markdown", data.get("content_html", validated_data["content"])
        )
        content_html = data.get("content_html")
        content_text = data.get("content_text")

        post = Post(
            title=validated_data["title"],
            slug=data.get(
                "slug", validated_data["slug"]
            ),  # Use provided slug or auto-generated
            content=content,
            content_html=content_html,
            content_text=content_text,
            preview=data.get("preview", validated_data.get("preview")),
            category=data.get("category", validated_data.get("category", "ostalo")),
            word_count=data.get("word_count", validated_data.get("word_count")),
            image_count=data.get("image_count", validated_data.get("image_count", 0)),
            images=data.get("images", validated_data.get("images", [])),
            author_id=current_user.id if current_user.is_authenticated else None,
            published=data.get("published", validated_data.get("published", True)),
        )

        # Ako je proslijeđen custom datum, koristi ga umjesto trenutnog
        if data.get("custom_date"):
            from datetime import datetime

            try:
                custom_datetime = datetime.fromisoformat(data.get("custom_date"))
                post.created_at = custom_datetime
            except ValueError:
                pass  # Ako format nije ispravan, koristi default

        db.session.add(post)
        db.session.commit()

        logger.info(f"Kreiran novi post: {post.title} (ID: {post.id})")

        return success_response(
            data={"id": post.id}, message="Post kreiran uspješno", status_code=201
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri kreiranju posta: {str(e)}", exc_info=True)
        return error_response("Greška pri kreiranju posta", status_code=500)


@api_bp.put("/posts/<int:post_id>")
@api_bp.put("/posts/<int:post_id>/")
@login_required
def update_post(post_id):
    """Update existing blog post"""
    logger.info(
        f"🔵 UPDATE POST {post_id}: User authenticated: {current_user.is_authenticated}"
    )
    logger.info(
        f"🔵 UPDATE POST {post_id}: User ID: {current_user.get_id() if current_user.is_authenticated else 'None'}"
    )
    try:
        post = Post.query.get_or_404(post_id)
        data = request.get_json()

        # Update fields
        post.title = data.get("title", post.title)
        post.slug = data.get("slug", post.slug)
        post.content = data.get(
            "content_markdown", data.get("content_html", post.content)
        )
        post.content_html = data.get("content_html", post.content_html)
        post.content_text = data.get("content_text", post.content_text)
        post.preview = data.get("preview", post.preview)
        post.category = data.get("category", post.category)
        post.word_count = data.get("word_count", post.word_count)
        post.image_count = data.get("image_count", post.image_count)
        post.images = data.get("images", post.images)
        post.published = data.get("published", post.published)

        # Ako je proslijeđen custom datum, ažuriraj created_at
        if data.get("custom_date"):
            from datetime import datetime

            try:
                custom_datetime = datetime.fromisoformat(data.get("custom_date"))
                post.created_at = custom_datetime
            except ValueError:
                pass  # Ako format nije ispravan, ne mijenjaj

        db.session.commit()

        logger.info(f"Ažuriran post: {post.title} (ID: {post.id})")

        return success_response(data={"id": post.id}, message="Post ažuriran uspješno")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri ažuriranju posta {post_id}: {str(e)}", exc_info=True)
        return error_response("Greška pri ažuriranju posta", status_code=500)


@api_bp.delete("/posts/<int:post_id>")
@api_bp.delete("/posts/<int:post_id>/")
@login_required
def delete_post(post_id):
    """Delete blog post"""
    try:
        post = Post.query.get_or_404(post_id)
        post_title = post.title  # Sačuvaj naslov za log

        db.session.delete(post)
        db.session.commit()

        logger.info(f"Obrisan post: {post_title} (ID: {post_id})")

        return success_response(message="Post obrisan uspješno")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Greška pri brisanju posta {post_id}: {str(e)}", exc_info=True)
        return error_response("Greška pri brisanju posta", status_code=500)
