from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.extensions import db
from app.models.plan_aktivnosti import PlanAktivnosti

plan_bp = Blueprint('plan_aktivnosti', __name__, url_prefix='/api/plan-aktivnosti')

# Redoslijed mjeseci za sortiranje
MONTHS_ORDER = {
    'JANUAR': 1, 'FEBRUAR': 2, 'MART': 3, 'APRIL': 4,
    'MAJ': 5, 'JUN': 6, 'JUL': 7, 'AVGUST': 8,
    'SEPTEMBAR': 9, 'OKTOBAR': 10, 'NOVEMBAR': 11, 'DECEMBAR': 12
}


@plan_bp.get('/')
@plan_bp.get('')
def get_all():
    """Dohvati sve aktivnosti, sortirane po mjesecu i redoslijedu"""
    try:
        aktivnosti = PlanAktivnosti.query.order_by(
            PlanAktivnosti.sort_order.asc(),
            PlanAktivnosti.id.asc()
        ).all()

        # Grupiši po mjesecima
        result = {}
        for a in aktivnosti:
            if a.month not in result:
                result[a.month] = []
            result[a.month].append(a.to_dict())

        # Sortiraj mjesece
        sorted_result = {}
        for month in sorted(result.keys(), key=lambda m: MONTHS_ORDER.get(m, 99)):
            sorted_result[month] = result[month]

        return jsonify({
            'success': True,
            'data': sorted_result,
            'total': len(aktivnosti)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@plan_bp.get('/flat')
def get_flat():
    """Dohvati sve aktivnosti kao flat listu (za admin panel)"""
    try:
        aktivnosti = PlanAktivnosti.query.order_by(
            PlanAktivnosti.sort_order.asc(),
            PlanAktivnosti.id.asc()
        ).all()

        return jsonify({
            'success': True,
            'aktivnosti': [a.to_dict() for a in aktivnosti],
            'total': len(aktivnosti)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@plan_bp.get('/<int:id>')
def get_one(id):
    """Dohvati jednu aktivnost"""
    try:
        aktivnost = PlanAktivnosti.query.get_or_404(id)
        return jsonify({'success': True, 'aktivnost': aktivnost.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Aktivnost nije pronađena'}), 404


@plan_bp.post('/')
@plan_bp.post('')
@login_required
def create():
    """Kreiraj novu aktivnost"""
    try:
        data = request.get_json()

        # Basic validation
        activity = (data.get('activity') or '').strip()
        if not activity:
            return jsonify({'success': False, 'error': 'Naziv aktivnosti je obavezan'}), 400

        month = (data.get('month') or '').strip()
        if not month:
            return jsonify({'success': False, 'error': 'Mjesec je obavezan'}), 400

        aktivnost = PlanAktivnosti(
            month=month.upper(),
            date=data.get('date', ''),
            activity=activity,
            organizer_guide=data.get('organizer_guide', ''),
            sort_order=MONTHS_ORDER.get(month.upper(), 1) * 100
        )

        db.session.add(aktivnost)
        db.session.commit()

        return jsonify({
            'success': True,
            'id': aktivnost.id,
            'message': 'Aktivnost kreirana uspješno'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@plan_bp.put('/<int:id>')
@login_required
def update(id):
    """Ažuriraj aktivnost"""
    try:
        aktivnost = PlanAktivnosti.query.get_or_404(id)
        data = request.get_json()

        aktivnost.month = data.get('month', aktivnost.month)
        aktivnost.date = data.get('date', aktivnost.date)
        aktivnost.activity = data.get('activity', aktivnost.activity)
        aktivnost.organizer_guide = data.get('organizer_guide', aktivnost.organizer_guide)

        if 'month' in data:
            aktivnost.sort_order = MONTHS_ORDER.get(data['month'], 1) * 100

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Aktivnost ažurirana uspješno'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@plan_bp.delete('/<int:id>')
@login_required
def delete(id):
    """Obriši aktivnost"""
    try:
        aktivnost = PlanAktivnosti.query.get_or_404(id)
        db.session.delete(aktivnost)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Aktivnost obrisana uspješno'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@plan_bp.post('/import')
@login_required
def import_json():
    """Importuj aktivnosti iz JSON strukture (briše postojeće!)"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'Nema podataka za import'}), 400

        # Obriši sve postojeće aktivnosti
        PlanAktivnosti.query.delete()

        count = 0
        for month, activities in data.items():
            if month in MONTHS_ORDER and isinstance(activities, list):
                for idx, act in enumerate(activities):
                    aktivnost = PlanAktivnosti(
                        month=month,
                        date=(act.get('date') or '').strip(),
                        activity=act.get('activity', ''),
                        organizer_guide=act.get('organizer_guide', ''),
                        sort_order=MONTHS_ORDER[month] * 100 + idx
                    )
                    db.session.add(aktivnost)
                    count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Importovano {count} aktivnosti',
            'count': count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@plan_bp.delete('/all')
@login_required
def delete_all():
    """Obriši sve aktivnosti"""
    try:
        count = PlanAktivnosti.query.delete()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Obrisano {count} aktivnosti',
            'count': count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
