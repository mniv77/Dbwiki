# ADD THIS ROUTE TO YOUR auth_routes.py

@app.route('/hagolem/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard - only accessible to admins"""
    return render_template('hagolem_admin.html')