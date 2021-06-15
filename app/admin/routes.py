from flask import render_template, flash, url_for, request
from flask_login import current_user, login_required
from werkzeug.utils import redirect

from app.models import User, Group
from app.admin import bp
from app.admin.forms import GroupForm, UserForm
from app import db
from commons import diff_array

@bp.route('/')
@login_required
def index():
    return render_template('a_index.html')

@bp.route('/groups')
@login_required
def groups():
    group_id = request.args.get('group_id')
    if not group_id or group_id == 0:
        groups = Group.query.all()
        return render_template('groups.html', groups=groups)
    else:
        group = Group.query.get(group_id)
        if not group:
            flash('Group with id={} is not found'.format(group_id))
            return redirect(url_for('admin.groups'))
        return render_template('group.html', group=group)

@bp.route('/add_group', methods=['GET', 'POST'])
@login_required
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group()
        group.name = form.name.data
        db.session.add(group)
        db.session.commit()
        flash('Group added.')
        return redirect(url_for('admin.groups'))
    return render_template('addgroup.html', form=form)

@bp.route('/edit_group/<groupid>', methods=['GET', 'POST'])
@login_required
def edit_group(groupid):
    form = GroupForm()
    group = Group.query.get(groupid)
    if not group:
        flash("Group with id={} is not found.".format(groupid))
        return redirect(url_for('admin.groups'))
    if form.validate_on_submit():
        group.name = form.name.data
        db.session.commit()
        flash('Group was saved.')
        return redirect(url_for('admin.groups'))
    else:
        form.name.data = group.name
        return render_template('editgroup.html', form=form)

@bp.route('/users')
@login_required
def users():
    u = User.query.all()
    return render_template('users.html', users=u)

@bp.route('/ban/<userid>')
@login_required
def ban(userid):
    user = User.query.get(userid)
    if not user:
        flash('User with id={} is not found'.format(userid))
        return redirect(url_for('admin.users'))
    user.is_blocked = not user.is_blocked
    db.session.commit()
    flash('Ban is changed to {}'.format(user.is_blocked))
    return redirect(url_for('admin.users'))

@bp.route('/edit_user/<userid>', methods=['GET', 'POST'])
@login_required
def edit_user(userid):
    user = User.query.get(userid)
    if not user:
        flash('User with id={} is not found'.format(userid))
        return redirect(url_for('admin.users'))
    form = UserForm()
    if form.validate_on_submit():
        # Get user
        # user = User.query.get(form.id.data)
        user.username = form.username.data
        user.email = form.email.data
        # check for changes in groups
        groupids_new = User.set_group_ids(form.groupids.data)
        groupids_old = User.set_group_ids(User.get_groups_ids(user))
        if groupids_new != groupids_old:
            # applying new groups
            new = diff_array(groupids_new, groupids_old)
            if new or len(new):
                for id in new:
                    group = Group.query.get(id)
                    user.add_to_group(group)
            old = diff_array(groupids_old, groupids_new)
            if old or len(old):
                for id in old:
                    group = Group.query.get(id)
                    user.remove_from_group(group)
        db.session.commit()
        return redirect(url_for('admin.users'))
    form.username.data = user.username
    form.email.data = user.email
    form.groupids.data = User.get_groups_ids(user)
    
    return render_template('edituser.html', form=form)

