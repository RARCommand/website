import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.models.bicycle import Bicycle, Category, BicycleSpecification
from app.extensions import db

admin = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Bicycle manage
@admin.route('/bicycles', methods=['GET', 'POST'])
@login_required
def manage_bicycles():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form.get('category_id')
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            image.save(image_path)
        else:
            flash('Unsupported image type!', 'danger')
            return redirect(url_for('admin.manage_bicycles'))

        # Bike creation
        bicycle = Bicycle(name=name, description=description, price=price, category_id=category_id, image_filename=filename)
        db.session.add(bicycle)
        db.session.commit()
        print(f"Bicycle added: {bicycle}")

        # adding specifications for bike
        spec_names = request.form.getlist('specification_name[]')
        spec_values = request.form.getlist('specification_value[]')
        for idx in range(len(spec_names)):
            new_spec = BicycleSpecification(bicycle_id=bicycle.id, name=spec_names[idx], value=spec_values[idx])
            db.session.add(new_spec)

        db.session.commit()
        flash('Nicycle was successfully added!', 'success')
        return redirect(url_for('admin.manage_bicycles'))

    categories = Category.query.all()
    bicycles = Bicycle.query.all()

    # Check if there are any bicycles in the database
    if not bicycles:
        flash('There is no any bicycles in database!', 'info')

    return render_template('admin/bicycles.html', bicycles=bicycles, categories=categories)


@admin.route('/bicycles/<int:bicycle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bicycle(bicycle_id):
    bicycle = Bicycle.query.get_or_404(bicycle_id)
    categories = Category.query.all()

    if request.method == 'POST':
        # updating the bike info
        bicycle.name = request.form['name']
        bicycle.description = request.form['description']
        bicycle.price = request.form['price']
        bicycle.category_id = request.form.get('category_id')

        # Updating existing specs and adding new
        spec_ids = request.form.getlist('specification_id[]')
        spec_names = request.form.getlist('specification_name[]')
        spec_values = request.form.getlist('specification_value[]')

        # creating a dictionary for easy search
        existing_specs = {str(spec.id): spec for spec in bicycle.specifications}

        for idx, spec_id in enumerate(spec_ids):
            if spec_id and spec_id in existing_specs:
                # update existing specs
                spec = existing_specs[spec_id]
                spec.name = spec_names[idx]
                spec.value = spec_values[idx]
            else:
                # adding new specs
                new_spec = BicycleSpecification(bicycle_id=bicycle.id, name=spec_names[idx], value=spec_values[idx])
                db.session.add(new_spec)

        db.session.commit()
        flash('Changes was saved!', 'success')
        return redirect(url_for('admin.manage_bicycles'))

    return render_template('admin/edit_bicycle.html', bicycle=bicycle, categories=categories)

@admin.route('/bicycles/<int:bicycle_id>/delete', methods=['POST'])
@login_required
def delete_bicycle(bicycle_id):
    bicycle = Bicycle.query.get_or_404(bicycle_id)
    db.session.delete(bicycle)
    db.session.commit()
    flash('Bicycle was successfully deleted!', 'success')
    return redirect(url_for('admin.manage_bicycles'))

# Manage categories
@admin.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        name = request.form['name']
        if name:
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
            flash('Category was successfully added!', 'success')
        else:
            flash('The name of category can not be empty!', 'danger')
        return redirect(url_for('admin.manage_categories'))

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.bicycles:
        flash('Can not delete category with bicycles!', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category was successfully deleted!', 'success')
    return redirect(url_for('admin.manage_categories'))