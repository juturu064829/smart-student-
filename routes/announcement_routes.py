from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Announcement
from utils.decorators import login_required, faculty_required, admin_required

announcement_bp = Blueprint('announcement', __name__, url_prefix='/announcements')

@announcement_bp.route('/')
@login_required
def index():
    user_role = session.get('user_role')
    category_filter = request.args.get('category', '').strip()

    query = Announcement.query

    if user_role == 'Student':
        query = query.filter(Announcement.target_role.in_(['All', 'Student']))
    elif user_role == 'Faculty':
        query = query.filter(Announcement.target_role.in_(['All', 'Faculty']))

    if category_filter:
        query = query.filter_by(category=category_filter)

    announcements = query.order_by(Announcement.created_at.desc()).all()

    return render_template(
        'announcements/index.html',
        announcements=announcements,
        selected_category=category_filter
    )

@announcement_bp.route('/add', methods=['POST'])
@faculty_required
def add_announcement():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    target_role = request.form.get('target_role', 'All')
    category = request.form.get('category', 'Academic')
    priority = request.form.get('priority', 'Normal')

    ann = Announcement(
        title=title,
        content=content,
        target_role=target_role,
        category=category,
        priority=priority,
        created_by_user_id=session.get('user_id')
    )
    db.session.add(ann)
    db.session.commit()
    flash('Announcement posted successfully!', 'success')
    return redirect(url_for('announcement.index'))

@announcement_bp.route('/delete/<int:ann_id>', methods=['POST'])
@admin_required
def delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'info')
    return redirect(url_for('announcement.index'))
