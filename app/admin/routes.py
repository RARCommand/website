import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from app.models.bicycle import Bicycle, Category, BicycleSpecification
from app.extensions import db

admin = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Управление велосипедами
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
            flash('Неподдерживаемый формат изображения!', 'danger')
            return redirect(url_for('admin.manage_bicycles'))

        # Создание велосипеда
        bicycle = Bicycle(name=name, description=description, price=price, category_id=category_id, image_filename=filename)
        db.session.add(bicycle)
        db.session.commit()
        print(f"Bicycle added: {bicycle}")

        # Добавление характеристик велосипеда
        spec_names = request.form.getlist('specification_name[]')
        spec_values = request.form.getlist('specification_value[]')
        for idx in range(len(spec_names)):
            new_spec = BicycleSpecification(bicycle_id=bicycle.id, name=spec_names[idx], value=spec_values[idx])
            db.session.add(new_spec)

        db.session.commit()
        flash('Велосипед успешно добавлен!', 'success')
        return redirect(url_for('admin.manage_bicycles'))

    categories = Category.query.all()
    bicycles = Bicycle.query.all()

    # Check if there are any bicycles in the database
    if not bicycles:
        flash('Нет доступных велосипедов в базе данных.', 'info')

    return render_template('admin/bicycles.html', bicycles=bicycles, categories=categories)


@admin.route('/bicycles/<int:bicycle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bicycle(bicycle_id):
    bicycle = Bicycle.query.get_or_404(bicycle_id)
    categories = Category.query.all()

    if request.method == 'POST':
        # Обновление данных велосипеда
        bicycle.name = request.form['name']
        bicycle.description = request.form['description']
        bicycle.price = request.form['price']
        bicycle.category_id = request.form.get('category_id')

        # Обновление существующих характеристик и добавление новых
        spec_ids = request.form.getlist('specification_id[]')
        spec_names = request.form.getlist('specification_name[]')
        spec_values = request.form.getlist('specification_value[]')

        # Создание словаря для удобного поиска характеристик по ID
        existing_specs = {str(spec.id): spec for spec in bicycle.specifications}

        for idx, spec_id in enumerate(spec_ids):
            if spec_id and spec_id in existing_specs:
                # Обновление существующей характеристики
                spec = existing_specs[spec_id]
                spec.name = spec_names[idx]
                spec.value = spec_values[idx]
            else:
                # Добавление новой характеристики
                new_spec = BicycleSpecification(bicycle_id=bicycle.id, name=spec_names[idx], value=spec_values[idx])
                db.session.add(new_spec)

        db.session.commit()
        flash('Изменения сохранены!', 'success')
        return redirect(url_for('admin.manage_bicycles'))

    return render_template('admin/edit_bicycle.html', bicycle=bicycle, categories=categories)

@admin.route('/bicycles/<int:bicycle_id>/delete', methods=['POST'])
@login_required
def delete_bicycle(bicycle_id):
    bicycle = Bicycle.query.get_or_404(bicycle_id)
    db.session.delete(bicycle)
    db.session.commit()
    flash('Велосипед успешно удален!', 'success')
    return redirect(url_for('admin.manage_bicycles'))

# Управление категориями
@admin.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        name = request.form['name']
        if name:
            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()
            flash('Категория успешно добавлена!', 'success')
        else:
            flash('Название категории не может быть пустым.', 'danger')
        return redirect(url_for('admin.manage_categories'))

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.bicycles:
        flash('Невозможно удалить категорию, содержащую велосипеды.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Категория успешно удалена!', 'success')
    return redirect(url_for('admin.manage_categories'))