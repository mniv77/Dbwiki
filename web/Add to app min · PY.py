# ============================================================================
# HAGOLEM WIKI ROUTES - ADD THIS TO YOUR app_min.py
# ============================================================================
# Add these routes after your existing routes (around line 550, before if __name__ == "__main__")

# --- WITHOUT Multi-User (Basic Wiki) ---
@app.route("/hagolem/wiki", endpoint="hagolem_wiki")
def hagolem_wiki():
    """HaGOLEM Ideas Wiki - Main page"""
    return render_template("hagolem_wiki.html")

# --- OR WITH Multi-User (Login Required) ---
# Uncomment these if you installed the multi-user system:

# from functools import wraps
# 
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             return redirect('/hagolem/login')
#         return f(*args, **kwargs)
#     return decorated_function
# 
# @app.route("/hagolem/wiki", endpoint="hagolem_wiki")
# @login_required
# def hagolem_wiki():
#     """HaGOLEM Ideas Wiki - Requires login"""
#     return render_template("hagolem_wiki.html")
# 
# @app.route("/hagolem/login", endpoint="hagolem_login")
# def hagolem_login():
#     """Login page for wiki"""
#     return render_template("hagolem_login.html")
# 
# @app.route("/hagolem/register", endpoint="hagolem_register")
# def hagolem_register():
#     """Registration page"""
#     return render_template("hagolem_register.html")
# 
# @app.route("/hagolem/admin", endpoint="hagolem_admin")
# @login_required
# def hagolem_admin():
#     """Admin dashboard"""
#     return render_template("hagolem_admin.html")

# ============================================================================
# API ROUTES FOR WIKI - ADD THESE TOO
# ============================================================================
# Copy all the routes from hagolem_wiki_routes.py and auth_routes.py here
# (The files you already have)