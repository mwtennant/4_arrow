"""User management routes and forms."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from typing import Union, List

from core.auth import auth_manager, AuthenticationError
from core.models import User
from core.profile import get_profile, edit_profile, delete_profile
from storage.database import db_manager
from src.commands.merge import merge_profiles
from src.commands.list_users import list_users
from .forms import CreateUserForm, SearchUserForm, EditProfileForm, DeleteProfileForm, MergeProfileForm, ListUsersForm
from .utils import require_auth

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@require_auth
def list() -> str:
    """List all users.
    
    Returns:
        Rendered user list template.
    """
    print("DEBUG: Accessing users list route")
    session = db_manager.get_session()
    try:
        users = session.query(User).order_by(User.last_name, User.first_name).all()
        print(f"DEBUG: Found {len(users)} users")
        return render_template('users/list.html', users=users)
    except Exception as e:
        print(f"DEBUG: Error in users list: {e}")
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('users/list.html', users=[])
    finally:
        session.close()


@users_bp.route('/create', methods=['GET', 'POST'])
@require_auth
def create() -> Union[str, redirect]:
    """Create a new user.
    
    Returns:
        Rendered create user template or redirect to user list.
    """
    form = CreateUserForm()
    
    if form.validate_on_submit():
        # Get database session
        session = db_manager.get_session()
        try:
            user = auth_manager.create_user(
                session,
                email=form.email.data,
                password="temp_password",  # Temporary password - user will need to login to change
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                address=form.address.data,
                usbc_id=form.usbc_id.data,
                tnba_id=form.tnba_id.data
            )
            
            flash(f'User {user.first_name} {user.last_name} created successfully!', 'success')
            return redirect(url_for('users.list'))
            
        except AuthenticationError as e:
            flash(str(e), 'error')
        finally:
            session.close()
    
    return render_template('users/create.html', form=form)


@users_bp.route('/<int:user_id>')
@require_auth
def view(user_id: int) -> str:
    """View a specific user.
    
    Args:
        user_id: ID of the user to view.
        
    Returns:
        Rendered user view template.
    """
    session = db_manager.get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('users.list'))
        
        return render_template('users/view.html', user=user)
    except Exception as e:
        flash(f'Error loading user: {str(e)}', 'error')
        return redirect(url_for('users.list'))
    finally:
        session.close()


@users_bp.route('/search', methods=['GET', 'POST'])
@require_auth
def search() -> Union[str, redirect]:
    """Search for users.
    
    Returns:
        Rendered search template or redirect to results.
    """
    form = SearchUserForm()
    users = []
    
    if form.validate_on_submit():
        session = db_manager.get_session()
        try:
            search_type = form.search_type.data
            search_value = form.search_value.data
            
            if search_type == 'user_id':
                try:
                    user_id = int(search_value)
                    user = get_profile(session=session, user_id=user_id)
                    users = [user] if user else []
                except ValueError:
                    flash('User ID must be a number.', 'error')
            elif search_type == 'email':
                user = get_profile(session=session, email=search_value)
                users = [user] if user else []
            elif search_type == 'usbc_id':
                user = get_profile(session=session, usbc_id=search_value)
                users = [user] if user else []
            elif search_type == 'tnba_id':
                user = get_profile(session=session, tnba_id=search_value)
                users = [user] if user else []
            elif search_type == 'name':
                # Search by name using list_users
                users = list_users(first=search_value) + list_users(last=search_value)
                # Remove duplicates
                seen = set()
                users = [user for user in users if user.id not in seen and not seen.add(user.id)]
            
            if not users:
                flash('No users found matching your search.', 'info')
                
        except Exception as e:
            flash(f'Error searching users: {str(e)}', 'error')
        finally:
            session.close()
    
    return render_template('users/search.html', form=form, users=users)


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@require_auth
def edit(user_id: int) -> Union[str, redirect]:
    """Edit a user profile.
    
    Args:
        user_id: ID of the user to edit.
        
    Returns:
        Rendered edit template or redirect to user view.
    """
    # Get user first to check if it exists
    session = db_manager.get_session()
    try:
        user = get_profile(session=session, user_id=user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('users.list'))
        
        form = EditProfileForm()
        
        if form.validate_on_submit():
            try:
                # Build update data
                update_data = {}
                if form.first_name.data:
                    update_data['first'] = form.first_name.data
                if form.last_name.data:
                    update_data['last'] = form.last_name.data
                if form.phone.data:
                    update_data['phone'] = form.phone.data
                if form.address.data:
                    update_data['address'] = form.address.data
                
                if update_data:
                    success = edit_profile(session=session, user_id=user_id, **update_data)
                    if success:
                        session.commit()
                        flash('Profile updated successfully!', 'success')
                        return redirect(url_for('users.view', user_id=user_id))
                    else:
                        flash('Failed to update profile.', 'error')
                else:
                    flash('No changes provided.', 'info')
                    
            except Exception as e:
                session.rollback()
                flash(f'Error updating profile: {str(e)}', 'error')
        
        # Pre-populate form with current data
        if request.method == 'GET':
            form.first_name.data = user.first_name
            form.last_name.data = user.last_name
            form.phone.data = user.phone
            form.address.data = user.address
        
        return render_template('users/edit.html', form=form, user=user)
    finally:
        session.close()


@users_bp.route('/<int:user_id>/delete', methods=['GET', 'POST'])
@require_auth
def delete(user_id: int) -> Union[str, redirect]:
    """Delete a user profile.
    
    Args:
        user_id: ID of the user to delete.
        
    Returns:
        Rendered delete template or redirect to user list.
    """
    # Get user first to check if it exists
    session = db_manager.get_session()
    try:
        user = get_profile(session=session, user_id=user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('users.list'))
        
        form = DeleteProfileForm()
        
        if form.validate_on_submit():
            try:
                success = delete_profile(session=session, user_id=user_id)
                if success:
                    session.commit()
                    flash(f'User {user.first_name} {user.last_name} deleted successfully!', 'success')
                    return redirect(url_for('users.list'))
                else:
                    flash('Failed to delete user.', 'error')
                    
            except Exception as e:
                session.rollback()
                flash(f'Error deleting user: {str(e)}', 'error')
        
        return render_template('users/delete.html', form=form, user=user)
    finally:
        session.close()


@users_bp.route('/merge', methods=['GET', 'POST'])
@require_auth
def merge() -> Union[str, redirect]:
    """Merge user profiles.
    
    Returns:
        Rendered merge template or redirect to user list.
    """
    form = MergeProfileForm()
    
    if form.validate_on_submit():
        session = db_manager.get_session()
        try:
            main_user_id = form.main_user_id.data
            merge_user_ids_str = form.merge_user_ids.data
            
            # Parse comma-separated user IDs
            merge_user_ids = []
            for id_str in merge_user_ids_str.split(','):
                try:
                    merge_user_ids.append(int(id_str.strip()))
                except ValueError:
                    flash(f'Invalid user ID: {id_str.strip()}', 'error')
                    return render_template('users/merge.html', form=form)
            
            # Verify main user exists
            main_user = get_profile(session=session, user_id=main_user_id)
            if not main_user:
                flash('Main user not found.', 'error')
                return render_template('users/merge.html', form=form)
            
            # Verify merge users exist
            merge_users = []
            for merge_id in merge_user_ids:
                user = get_profile(session=session, user_id=merge_id)
                if not user:
                    flash(f'User ID {merge_id} not found.', 'error')
                    return render_template('users/merge.html', form=form)
                merge_users.append(user)
            
            # Perform merge
            merge_profiles(main_user_id, merge_user_ids)
            
            flash(f'Successfully merged {len(merge_user_ids)} profile(s) into {main_user.first_name} {main_user.last_name}!', 'success')
            return redirect(url_for('users.view', user_id=main_user_id))
            
        except Exception as e:
            flash(f'Error merging profiles: {str(e)}', 'error')
        finally:
            session.close()
    
    return render_template('users/merge.html', form=form)


@users_bp.route('/filter', methods=['GET', 'POST'])
@require_auth
def filter() -> str:
    """Filter users with advanced options.
    
    Returns:
        Rendered filter template.
    """
    form = ListUsersForm()
    users = []
    
    if form.validate_on_submit():
        try:
            # Build filter parameters
            filters = {}
            if form.first_name.data:
                filters['first'] = form.first_name.data
            if form.last_name.data:
                filters['last'] = form.last_name.data
            if form.email.data:
                filters['email'] = form.email.data
            if form.phone.data:
                filters['phone'] = form.phone.data
            if form.address.data:
                filters['address'] = form.address.data
            if form.usbc_id.data:
                filters['usbc_id'] = form.usbc_id.data
            if form.tnba_id.data:
                filters['tnba_id'] = form.tnba_id.data
            
            users = list_users(**filters)
            
            if not users:
                flash('No users found matching your filters.', 'info')
                
        except Exception as e:
            flash(f'Error filtering users: {str(e)}', 'error')
    
    return render_template('users/filter.html', form=form, users=users)