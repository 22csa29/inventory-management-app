from flask import Flask, redirect, render_template, request, flash, url_for
import mysql.connector
from mysql.connector import errors
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_random_secret'  # needed for flash()

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Magudeesh@07',
    'database': 'Inventory'
}

def get_connection():
    return mysql.connector.connect(**db_config)

# ─── Products ────────────────────────────────────────────────────────────────

@app.route('/')
@app.route('/products')
def show_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    conn.close()
    return render_template('product.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    pid = request.form['product_id']
    name = request.form['product_name']
    qty = request.form['product_quantity']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Product (product_id, product_name, product_quantity) VALUES (%s, %s, %s)",
            (pid, name, qty)
        )
        conn.commit()
        flash(f"Product {pid} added successfully!", "success")
    except errors.IntegrityError as e:
        flash(f"Failed to add Product {pid}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_products'))

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    name = request.form['product_name']
    qty = request.form['product_quantity']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Product SET product_name=%s, product_quantity=%s WHERE product_id=%s",
            (name, qty, product_id)
        )
        conn.commit()
        flash(f"Product {product_id} updated!", "success")
    except errors.DatabaseError as e:
        flash(f"Failed to update Product {product_id}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_products'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Product WHERE product_id=%s", (product_id,))
        conn.commit()
        flash(f"Product {product_id} deleted.", "success")
    except errors.IntegrityError as e:
        flash(f"Cannot delete Product {product_id}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_products'))


# ─── Locations ───────────────────────────────────────────────────────────────

@app.route('/locations')
def show_locations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Location")
    locations = cursor.fetchall()
    conn.close()
    return render_template('location.html', locations=locations)

@app.route('/add_location', methods=['POST'])
def add_location():
    lid = request.form['location_id']
    name = request.form['location_name']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Location (location_id, location_name) VALUES (%s, %s)",
            (lid, name)
        )
        conn.commit()
        flash(f"Location {lid} added!", "success")
    except errors.IntegrityError as e:
        flash(f"Failed to add Location {lid}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_locations'))

@app.route('/update_location/<int:location_id>', methods=['POST'])
def update_location(location_id):
    name = request.form['location_name']
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Location SET location_name=%s WHERE location_id=%s",
            (name, location_id)
        )
        conn.commit()
        flash(f"Location {location_id} updated!", "success")
    except errors.DatabaseError as e:
        flash(f"Failed to update Location {location_id}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_locations'))

@app.route('/delete_location/<int:location_id>', methods=['POST'])
def delete_location(location_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Location WHERE location_id=%s", (location_id,))
        conn.commit()
        flash(f"Location {location_id} deleted.", "success")
    except errors.IntegrityError as e:
        flash(f"Cannot delete Location {location_id}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_locations'))


# ─── Product Movements ──────────────────────────────────────────────────────

@app.route('/movements')
def show_movements():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" 
        SELECT
          pm.movement_id,
          pm.timestamp,
          fl.location_name AS from_location,
          tl.location_name AS to_location,
          p.product_name AS product,
          pm.qty
        FROM ProductMovement pm
        LEFT JOIN Location fl ON pm.from_location = fl.location_id
        LEFT JOIN Location tl ON pm.to_location   = tl.location_id
        JOIN Product p       ON pm.product_id      = p.product_id
        ORDER BY pm.timestamp DESC
    """)
    movements = cursor.fetchall()

    cursor.execute("SELECT product_id, product_name FROM Product")
    products = cursor.fetchall()
    cursor.execute("SELECT location_id, location_name FROM Location")
    locations = cursor.fetchall()
    conn.close()

    return render_template(
        'productmovement.html',
        movements=movements,
        products=products,
        locations=locations
    )

@app.route('/add_movement', methods=['POST'])
def add_movement():
    mid = request.form['movement_id']
    frm = request.form.get('from_location') or None
    to = request.form.get('to_location') or None
    pid = request.form['product_id']
    qty = request.form['qty']
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO ProductMovement
              (movement_id, timestamp, from_location, to_location, product_id, qty)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (mid, ts, frm, to, pid, qty))
        conn.commit()
        flash(f"Movement {mid} recorded!", "success")
    except errors.IntegrityError as e:
        flash(f"Failed to record Movement {mid}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_movements'))

@app.route('/update_movement/<int:movement_id>', methods=['POST'])
def update_movement(movement_id):
    frm = request.form.get('from_location') or None
    to = request.form.get('to_location') or None
    pid = request.form['product_id']
    qty = request.form['qty']
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ProductMovement
            SET timestamp=%s, from_location=%s, to_location=%s, product_id=%s, qty=%s
            WHERE movement_id=%s
        """, (ts, frm, to, pid, qty, movement_id))
        conn.commit()
        flash(f"Movement {movement_id} updated!", "success")
    except errors.DatabaseError as e:
        flash(f"Failed to update Movement {movement_id}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_movements'))

@app.route('/delete_movement/<int:movement_id>', methods=['POST'])
def delete_movement(movement_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ProductMovement WHERE movement_id=%s", (movement_id,))
        conn.commit()
        flash(f"Movement {movement_id} deleted.", "success")
    except errors.DatabaseError as e:
        flash(f"Cannot delete Movement {movement_id}: {e.msg}", "error")
    finally:
        conn.close()
    return redirect(url_for('show_movements'))


# ─── Report ─────────────────────────────────────────────────────────────────
@app.route('/report')
def inventory_report():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.product_name AS product,
            l.location_name AS warehouse,
            p.product_quantity
              + IFNULL(SUM(CASE WHEN pm.to_location = l.location_id THEN pm.qty ELSE 0 END), 0)
              - IFNULL(SUM(CASE WHEN pm.from_location = l.location_id THEN pm.qty ELSE 0 END), 0) AS balance
        FROM Product p
        JOIN Location l
        LEFT JOIN ProductMovement pm 
            ON pm.product_id = p.product_id
            AND (pm.from_location = l.location_id OR pm.to_location = l.location_id)
        WHERE EXISTS (SELECT 1 FROM ProductMovement pm_check WHERE pm_check.product_id = p.product_id)
        GROUP BY p.product_name, l.location_name, p.product_quantity
        HAVING balance > 0
        ORDER BY p.product_name, l.location_name;
    """)
    rows = cursor.fetchall()
    conn.close()

    return render_template('report.html', rows=rows)



if __name__ == '__main__':
    app.run(debug=True)
