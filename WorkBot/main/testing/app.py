from flask import Flask, render_template, request, redirect, url_for, flash
from backend.workbot.WorkBot import WorkBot

app = Flask(__name__)
app.secret_key = "change_this_secret"
bot = WorkBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download_orders', methods=['POST'])
def download_orders():
    stores = request.form.getlist('stores')
    vendors = request.form.getlist('vendors')
    try:
        bot.download_orders(stores, vendors)
        flash("Orders downloaded successfully.", "success")
    except Exception as e:
        flash(f"Error downloading orders: {e}", "danger")
    return redirect(url_for('index'))

@app.route('/list_orders', methods=['POST'])
def list_orders():
    stores = request.form.getlist('stores')
    vendors = request.form.getlist('vendors')
    orders = bot.get_orders(stores, vendors)
    return render_template('index.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
