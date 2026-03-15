from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.extensions import db
from app.models.trail import Trail

trails_bp = Blueprint("trails", __name__, url_prefix="/api/trails")


@trails_bp.get("/")
@trails_bp.get("")
def get_trails():
    """Get all published trails with pagination"""
    try:
        # Pagination params
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 50)

        # Query
        query = Trail.query.filter_by(published=True).order_by(Trail.name.asc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        trails_list = [t.to_dict() for t in pagination.items]

        return jsonify(
            {
                "trails": trails_list,
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
        )
    except Exception as e:
        return jsonify({"error": str(e), "trails": []}), 500


@trails_bp.get("/<int:trail_id>")
def get_trail(trail_id):
    """Get single trail"""
    try:
        trail = Trail.query.get_or_404(trail_id)
        return jsonify(trail.to_dict())
    except Exception as e:
        return jsonify({"error": "Trail not found"}), 404


@trails_bp.post("/")
@trails_bp.post("")
@login_required
def create_trail():
    """Create new trail"""
    try:
        data = request.get_json()

        trail = Trail(
            name=data.get("name"),
            description=data.get("description"),
            difficulty=data.get("difficulty", "Srednja"),
            distance_km=data.get("distance_km"),
            duration_hours=data.get("duration_hours"),
            elevation_gain_m=data.get("elevation_gain_m"),
            start_point=data.get("start_point"),
            end_point=data.get("end_point"),
            region=data.get("region"),
            images=data.get("images", []),
            gpx_file=data.get("gpx_file"),
            water_sources=data.get("water_sources", False),
            shelters=data.get("shelters", False),
            scenic_views=data.get("scenic_views", False),
            features=data.get("features", []),
            equipment=data.get("equipment", []),
            warning=data.get("warning", ""),
            contact=data.get("contact", "+387 65 581 354"),
            published=data.get("published", True),
        )

        db.session.add(trail)
        db.session.commit()

        return (
            jsonify(
                {"success": True, "id": trail.id, "message": "Trail kreiran uspješno"}
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@trails_bp.put("/<int:trail_id>")
@login_required
def update_trail(trail_id):
    """Update trail"""
    try:
        trail = Trail.query.get_or_404(trail_id)
        data = request.get_json()

        trail.name = data.get("name", trail.name)
        trail.description = data.get("description", trail.description)
        trail.difficulty = data.get("difficulty", trail.difficulty)
        trail.distance_km = data.get("distance_km", trail.distance_km)
        trail.duration_hours = data.get("duration_hours", trail.duration_hours)
        trail.elevation_gain_m = data.get("elevation_gain_m", trail.elevation_gain_m)
        trail.start_point = data.get("start_point", trail.start_point)
        trail.end_point = data.get("end_point", trail.end_point)
        trail.region = data.get("region", trail.region)
        trail.images = data.get("images", trail.images)
        trail.gpx_file = data.get("gpx_file", trail.gpx_file)
        trail.water_sources = data.get("water_sources", trail.water_sources)
        trail.shelters = data.get("shelters", trail.shelters)
        trail.scenic_views = data.get("scenic_views", trail.scenic_views)
        trail.features = data.get("features", trail.features)
        trail.equipment = data.get("equipment", trail.equipment)
        trail.warning = data.get("warning", trail.warning)
        trail.contact = data.get("contact", trail.contact)
        trail.published = data.get("published", trail.published)

        db.session.commit()

        return jsonify({"success": True, "message": "Trail ažuriran uspješno"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@trails_bp.delete("/<int:trail_id>")
@login_required
def delete_trail(trail_id):
    """Delete trail"""
    try:
        trail = Trail.query.get_or_404(trail_id)
        db.session.delete(trail)
        db.session.commit()

        return jsonify({"success": True, "message": "Trail obrisan uspješno"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
