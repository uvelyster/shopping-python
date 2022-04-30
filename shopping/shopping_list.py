#
# Introducing MySQL InnoDB Cluster
#
# This file contains the sample Python + Flask application for demonstrating
# how to build a simple application with InnoDB Cluster.
#
# The application is a simple shopping list that users can use to make a list
# of things to purchase. This base application can be expanded and modified to
# manage a set of lists should you decide to experiment or embellish for
# curiosity.
#
# The application requires the following files in the directories indicated.
#
# <root>\shopping_list.py             : main Python script
# <root>\database\shopping_db.sql     : SQL file for creating the initial data
# <root>\database\shopping_lib.py     : Python library for working with database
# <root>\templates\404.html           : page/link not found error template
# <root>\templates\500.html           : custom error template
# <root>\templates\base.html          : base template for all templates/forms
# <root>\templates\list.html          : shopping list template
#
# Dr. Charles Bell, 2018
#
from flask import Flask, render_template, request, redirect, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import (HiddenField, TextField, SelectField,
                     SelectMultipleField, IntegerField, SubmitField)
from wtforms.validators import Required, Length
from database.shopping_lib import Library, ShoppingList

#
# Strings
#
REQUIRED = "{0} field is required."
RANGE = "{0} range is {1} to {2} characters."

#
# Setup Flask, Bootstrap, and security.
#
app = Flask(__name__)
app.config['SECRET_KEY'] = "He says, he's already got one!"
manager = Manager(app)
bootstrap = Bootstrap(app)

#
# Setup the library database class
#
# Provide your user credentials here
library = Library()

#
# Utility functions
#
def flash_errors(form):
    for error in form.errors:
        flash("{0} : {1}".format(error, ",".join(form.errors[error])))
        
#
# Form classes - the forms for the application
#
class ListForm(FlaskForm):
    submit = SubmitField('New')
    hide_checked = SubmitField('Refresh')
    show_all = SubmitField('Show All')

class ItemForm(FlaskForm):
    row_id = HiddenField('Id')
    description = TextField('Description', validators=[
            Required(message=REQUIRED.format("Description")),
            Length(min=1, max=64, message=RANGE.format("Description", 1, 64))
        ])
    note = TextField( 'Note')
    create_button = SubmitField('Add')

#
# Routing functions - the following defines the routing functions for the
# application.
# 

#
# Shopping List
#
# This is the default page for "home" and listing rows in the database.
# 
@app.route('/', methods=['GET', 'POST'])
def shopping_list(row_id=None):
    rows = []
    columns = []
    form = ListForm()
    if request.method == 'POST':
        if form.submit.data:
            return redirect('item')
        elif form.hide_checked.data:
            # returns list of all checkboxes
            checkboxes = request.form.getlist('checkboxes')
            # returns a list of values that were checked
            list_row_ids = request.form.getlist('row_ids')
            for list_row_id in list_row_ids:
                shopping_list_db = ShoppingList(library)
                purchased_value = (0, 1)[list_row_id in checkboxes]
                shopping_list_db.update_purchased(list_row_id, purchased_value)
                print(">>> Setting purchased = {1} for rowid = {0}.".format(list_row_id, purchased_value))
            rows = library.get_list(False)            
        else:
            rows = library.get_list()
    else:
        # Default is to get all items
        rows = library.get_list()
    columns = (
        '<td style="width:200px">Description</td>',
        '<td style="width:200px">Note</td>',
        '<td style="width:80px">Purchased?</td>',
    )
    return render_template("list.html", form=form, rows=rows,
                           columns=columns)


#
# Item View
#
# This is the default page for adding, updating, and deleting items in the list.
# 
@app.route('/item', methods=['GET', 'POST'])
def item_view(row_id=None):
    operation = request.args.get("operation", "Add")
    row_id = request.args.get("row_id")
    shopping_list_db = ShoppingList(library)
    form = ItemForm()
    # Get data from the form if present
    form_row_id = form.row_id.data
    form_description = form.description.data
    form_note = form.note.data
    form.create_button.label.text = operation
    # If the route with the variable is called, retrieve the data item
    # and populate the form. 
    if row_id:
        data = shopping_list_db.read(row_id)
        if data == []:
            flash("Item not found!")
        form.row_id.data = row_id
        form.description.data = data[0][1]
        form.note.data = data[0][2]
    if request.method == 'POST':
        # First, determine if we must create, update, or delete when form posts.
        if form.create_button.data:
            if form.create_button.label.text == "Update":
                operation = "Update"
            elif form.create_button.label.text == "Delete":
                operation = "Delete"
        if form.validate_on_submit():
            # Get the data from the form here
            if operation == "Add":
                try:
                    shopping_list_db.create(form_description, form_note)
                    flash("Added.")
                except Exception as err:
                    flash(err)
            elif operation == "Update":
                try:
                    print(">>> {0}".format(form.row_id.data))
                    shopping_list_db.update(form_row_id, form_description, form_note)
                    flash("Updated.")
                except Exception as err:
                    flash(err)
            else:
                try:
                    shopping_list_db.delete(form_row_id)
                    flash("Deleted.")
                except Exception as err:
                    flash(err)
            return redirect('/')
        else:
            flash_errors(form)
    return render_template("item.html", form=form)

#
# Error handling routes
# 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#
# Main entry
#
if __name__ == '__main__':
    manager.run()
