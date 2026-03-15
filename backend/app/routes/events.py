from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.event import Event
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix='/api/events')


@events_bp.get('/')
@events_bp.get('')
def get_events():
    """Get all published events"""
    try:
        events = Event.query.filter_by(published=True).order_by(Event.event_date.asc()).all()
        return jsonify({'events': [e.to_dict() for e in events]})
    except Exception as e:
        return jsonify({'error': str(e), 'events': []}), 500


@events_bp.get('/<int:event_id>')
def get_event(event_id):
    """Get single event"""
    try:
        event = Event.query.get_or_404(event_id)
        return jsonify(event.to_dict())
    except Exception as e:
        return jsonify({'error': 'Event not found'}), 404


@events_bp.post('/')
@events_bp.post('')
@login_required
def create_event():
    """Create new event"""
    try:
        data = request.get_json()

        event = Event(
            title=data.get('title'),
            description=data.get('description'),
            event_date=datetime.strptime(data.get('event_date'), '%Y-%m-%d').date(),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            max_participants=data.get('max_participants'),
            activity_type=data.get('activity_type'),
            difficulty=data.get('difficulty'),
            location=data.get('location'),
            published=data.get('published', True),
        )

        db.session.add(event)
        db.session.commit()

        return jsonify({
            'success': True,
            'id': event.id,
            'message': 'Event kreiran uspješno'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@events_bp.put('/<int:event_id>')
@login_required
def update_event(event_id):
    """Update event"""
    try:
        event = Event.query.get_or_404(event_id)
        data = request.get_json()

        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)

        if data.get('event_date'):
            event.event_date = datetime.strptime(data.get('event_date'), '%Y-%m-%d').date()

        event.start_time = data.get('start_time', event.start_time)
        event.end_time = data.get('end_time', event.end_time)
        event.max_participants = data.get('max_participants', event.max_participants)
        event.activity_type = data.get('activity_type', event.activity_type)
        event.difficulty = data.get('difficulty', event.difficulty)
        event.location = data.get('location', event.location)
        event.published = data.get('published', event.published)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Event ažuriran uspješno'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@events_bp.delete('/<int:event_id>')
@login_required
def delete_event(event_id):
    """Delete event"""
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Event obrisan uspješno'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
