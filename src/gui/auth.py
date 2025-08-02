"""Authentication routes and session management."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from typing import Union

from core.auth import auth_manager, AuthenticationError
from storage.database import db_manager
from .forms import LoginForm, SignupForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, redirect]:
    """Handle user login.
    
    Returns:
        Rendered login template or redirect to index.
    """
    # If already logged in, redirect to index
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = LoginForm()
    print(f"DEBUG: Form created: {form}")
    print(f"DEBUG: Form fields: {[field.name for field in form]}")
    
    if form.validate_on_submit():
        # Get database session
        db_session = db_manager.get_session()
        try:
            user = auth_manager.authenticate_user(
                db_session, 
                form.email.data, 
                form.password.data
            )
            session['user_id'] = user.id
            session['user_name'] = f"{user.first_name} {user.last_name}"
            session.permanent = True
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('index'))
            
        except AuthenticationError as e:
            flash(str(e), 'error')
        finally:
            db_session.close()
    
    print(f"DEBUG: Rendering login.html with form: {form}")
    return render_template('login.html', form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup() -> Union[str, redirect]:
    """Handle user signup.
    
    Returns:
        Rendered signup template or redirect to login.
    """
    # If already logged in, redirect to index
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = SignupForm()
    
    if form.validate_on_submit():
        # Get database session
        db_session = db_manager.get_session()
        try:
            user = auth_manager.create_user(
                db_session,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone=form.phone.data,
                address=form.address.data,
                usbc_id=form.usbc_id.data,
                tnba_id=form.tnba_id.data
            )
            
            flash(f'Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except AuthenticationError as e:
            flash(str(e), 'error')
        finally:
            db_session.close()
    
    return render_template('signup.html', form=form)


@auth_bp.route('/logout')
def logout() -> redirect:
    """Handle user logout.
    
    Returns:
        Redirect to login page.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))