"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Login (PIN access)

 Version : 0.1
===========================================================
"""

from flask import Blueprint, redirect, render_template, request, session

from services import settings_service


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        pin = request.form.get("pin", "")

        if settings_service.check_pin(pin):
            session["authenticated"] = True
            return redirect(request.args.get("next") or "/")

        error = "Неверный PIN"

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect("/login")
