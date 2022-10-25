from flask import render_template, url_for, request, redirect, flash, session
from diary import app, db
from diary.models import User, Entry, Project
from diary.forms import RegistrationForm, LoginForm, AddDiaryEntry, AddProject
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import extract
from datetime import datetime, timedelta
#pydrive imports
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

#Main Pages accessed from navbar
@app.route("/")
@app.route("/home", methods= ['GET', 'POST'])
def home():
    user_id = current_user.get_id()
    page = request.args.get('page',1,type=int)
    search = request.args.get('search')
    if search:
        entries = Entry.query.filter(Entry.date.contains(search) | Entry.entry_text.contains(search) | Entry.tags.contains(search))
        entries = entries.order_by(Entry.date.desc()).paginate(page=page, per_page=3)
    else:
        entries = Entry.query.filter_by(author_id=user_id).order_by(Entry.date.desc()).paginate(page=page, per_page=3)
    next_url = url_for('home', page=entries.next_num) \
        if entries.has_next else None
    prev_url = url_for('home', page=entries.prev_num) \
        if entries.has_prev else None
    return render_template('home.html', title='Home', entries=entries.items, user_id=user_id, next_url=next_url, prev_url=prev_url)

@app.route("/calendar")
def calendar():
    user_id = current_user.get_id()
    query = request.args.get('query')
#Grabs current datetime and seperates into month and year
    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_year = current_datetime.year
    month_dict= { 1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}
#Query for previous page link will -1 from month counter unless it is the first month
    if query=='minus':
        if session["month_counter"] == 1:
            session["month_counter"] = 12
            session["year_counter"] -= 1
        else:
            session["month_counter"] -= 1
        return redirect(url_for('calendar'))
#Query for next page will +1 to month counter unless it is last month
    if query=='plus':
        if session["month_counter"] == 12:
            session["month_counter"] = 1
            session["year_counter"] += 1
        else:
            session["month_counter"] += 1
        return redirect(url_for('calendar'))
#Resets using current datetime if user wants to return to current month
    if query=='current':
        session["month_counter"] = current_month
        session["year_counter"] = current_year
        return redirect(url_for('calendar'))
    entries = Entry.query.filter_by(author_id=user_id).filter(extract('month', Entry.date) == session["month_counter"]).filter(extract('year', Entry.date) == session["year_counter"]).order_by(Entry.date.desc())
    month_name = month_dict[(session["month_counter"])]
#Simple search function included using get request
    search = request.args.get('search')
    if search:
        entries = Entry.query.filter(Entry.date.contains(search) | Entry.entry_text.contains(search) | Entry.tags.contains(search)).order_by(Entry.date.desc())
    return render_template('calendar.html', title='Calendar', entries=entries, user_id=user_id, year=session["year_counter"], month_name=month_name, search=search)

#Project related pages
@app.route("/project_hub", methods= ['GET', 'POST'])
def project_hub():
    user_id = current_user.get_id()
    search = request.args.get('search')
#Simple pagination added for 3 projects to be displayed per page, with dynamic links created
    page = request.args.get('page',1,type=int)
    if search:
        projects = Project.query.filter(Project.date_created.contains(search) | Project.project_title.contains(search) | Project.project_description.contains(search) |  Project.project_type.contains(search)).order_by(Project.date_created.desc())
        projects = projects.order_by(Project.date_created.desc()).paginate(page=page, per_page=3)
    else:
        projects = Project.query.filter_by(author_id=user_id).order_by(Project.date_created.desc()).paginate(page=page, per_page=3)
    next_url = url_for('project_hub', page=projects.next_num) \
        if projects.has_next else None
    prev_url = url_for('project_hub', page=projects.prev_num) \
        if projects.has_prev else None
    return render_template('project_hub.html', title='Project Hub', user_id=user_id, projects=projects.items, search=search, next_url=next_url, prev_url=prev_url)

@app.route("/project/<int:project_id>", methods= ['GET', 'POST'])
def project(project_id):
    project = Project.query.get_or_404(project_id)
    project_title = project.project_title
    entries = Entry.query.filter_by(related_project=project_title).order_by(Entry.date.desc()).all()
    return render_template('individual_project.html', project=project, entries=entries, id=id)

#G Drive Authentication Flow
@app.route("/authentication/<int:project_id>", methods= ['GET'])
def authentication(project_id):
    project = Project.query.get_or_404(project_id)
    id = project.google_drive
    # Creates local webserver and auto handles authentication.
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    # Create GoogleDrive instance with authenticated GoogleAuth instance.
    drive = GoogleDrive(gauth)
    return redirect('https://docs.google.com/document/d/'+id+'/edit')

@app.route("/new_project", methods= ['GET', 'POST'])
def new_project():
    form=AddProject()
    if form.validate_on_submit():
        current_datetime = datetime.now()
        user_id = current_user.get_id()
        project = Project(project_title=form.project_title.data, project_description=form.project_description.data, project_type=form.project_type.data, total_words_goal=form.total_words_goal.data, total_words_current=form.total_words_current.data, weekly_words_goal=form.weekly_words_goal.data, weekly_words_current=form.weekly_words_current.data, google_drive=form.google_drive.data, author_id=user_id, date_created=current_datetime)
        db.session.add(project)
        db.session.commit()
        flash(u'Your project has been created!')
        return redirect(url_for('project', project_id=project.project_id))
    return render_template('new_project.html', title='New Project', form=form)

@app.route("/edit_project/<int:project_id>", methods= ['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get(project_id)
#Autofills form using the project object so that some elements can be edited without changing others
    form=AddProject(obj=project)
    if form.validate_on_submit():
        project.project_title=form.project_title.data
        project.project_description=form.project_description.data
        project.project_type=form.project_type.data
        project.total_words_goal=form.total_words_goal.data
        project.total_words_current=form.total_words_current.data
        project.weekly_words_goal=form.weekly_words_goal.data
        project.weekly_words_current=form.weekly_words_current.data
        project.google_drive=form.google_drive.data
        db.session.commit()
        return redirect(url_for('project', project_id=project.project_id))
    return render_template('edit_project.html', project=project, form=form)

@app.route("/successful_project_edit")
def successful_project_edit():
    return render_template('successful_project_edit.html', title="You have successfully edited this project!"), {"Refresh": "5; home"}

@app.route("/project/confirm_delete_project/<int:project_id>", methods=['GET', 'POST'])
def confirm_delete_project(project_id):
    project = Project.query.get(project_id)
    entries = Entry.query.filter_by(related_project=project.project_title).order_by(Entry.date.desc()).all()
    return render_template('confirm_delete_project.html', project=project, entries=entries)

@app.route("/project/delete/<int:project_id>", methods=['GET','POST'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    entries = Entry.query.filter_by(related_project=project.project_title).order_by(Entry.date.desc()).all()
    db.session.delete(project)
    for entry in entries:
        db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('successful_project_delete'))

@app.route("/successful_project_delete")
def successful_project_delete():
    return render_template('successful_project_delete.html', title="You have successfully deleted this project!"), {"Refresh": "2; home"}

#Journal entry related pages
@app.route("/new_entry", methods= ['GET', 'POST'])
def new_entry():
    form=AddDiaryEntry()
    user_id = current_user.get_id()
#If entry is created from a project page, it passes the project title into the related_project field automatically
    title = request.args.get('title')
    if title:
        form.related_project.choices = [title]
#Else it displays all current projects
    else:
        form.related_project.choices = [(project.project_title) for project in Project.query.filter_by(author_id=user_id).all()]
    if form.validate_on_submit():
        current_datetime = datetime.now()
        entry = Entry(entry_text=form.entry_text.data, related_project=form.related_project.data, tags=form.tags.data, author_id=user_id, date=current_datetime)
        db.session.add(entry)
        db.session.commit()
        flash(u'Your entry has been recorded!')
        return redirect(url_for('entry', entry_id=entry.entry_id))
    return render_template('new_entry.html', title='New Entry', form=form)

@app.route("/edit_entry/<int:entry_id>", methods= ['GET', 'POST'])
def edit_entry(entry_id):
    entry = Entry.query.get(entry_id)
#Editing an entry pre-populates form from the entry object
    form=AddDiaryEntry(obj=entry)
    user_id = current_user.get_id()
    form.related_project.choices = [(project.project_title) for project in Project.query.filter_by(author_id=user_id).all()]
    if form.validate_on_submit():
        entry.entry_text=form.entry_text.data
        entry.related_project=form.related_project.data
        entry.tags=form.tags.data
        db.session.commit()
        flash(u'Your entry has been edited!')
        return redirect(url_for('entry', entry_id=entry.entry_id))
    return render_template('edit_entry.html', entry=entry, form=form)

@app.route("/successful_entry_edit")
def successful_entry_edit():
    return render_template('successful_entry_edit.html', title="You have successfully edited this entry!"), {"Refresh": "2; entry; entry_id=entry.entry_id"}

@app.route("/entry/confirm_delete_entry/<int:entry_id>", methods=['GET', 'POST'])
def confirm_delete_entry(entry_id):
    entry = Entry.query.get(entry_id)
    return render_template('confirm_delete_entry.html', entry=entry)

@app.route("/entry/delete/<int:entry_id>", methods=['GET','POST'])
def delete_entry(entry_id):
    entry = Entry.query.get(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('successful_entry_delete'))

@app.route("/successful_entry_delete")
def successful_entry_delete():
    return render_template('successful_entry_delete.html', title="You have successfully deleted this entry!"), {"Refresh": "5; home"}


@app.route("/entry/<int:entry_id>")
def entry(entry_id):
    user_id = current_user.get_id()
    current_entry_id = entry_id
    entry = Entry.query.get_or_404(entry_id)
    entry_project = entry.related_project
    project = Project.query.filter_by(project_title=entry_project, author_id=user_id).first()
#Passes a list of all other entries tagged to the same project to the page so these can be displayed below
    related_entries = Entry.query.filter(Entry.entry_id != current_entry_id).filter_by(related_project=entry_project, author_id=user_id).order_by(Entry.date.desc()).all()
    rel_length = (len(related_entries))
    return render_template('individual_entry.html', date=entry.date, entry=entry, project=project, related_entries=related_entries, rel_length=rel_length)

#Redundant, could be built upon?
@app.route("/individual_day")
def individual_day():
    return render_template('individual_day.html', title="Individual Day")


#Register and Login related pages
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('successful_login'))
        flash('Invalid email address or password.')
    return render_template('login.html', title='Login', form=form)

@app.route("/successful_login")
def successful_login():
    return render_template('successful_login.html', title="You are now logged in!"), {"Refresh": "3; home"}

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('successful_logout'))

@app.route("/successful_logout")
def successful_logout():
    return render_template('successful_logout.html', title="You have successfully logged out!"), {"Refresh": "3; home"}
