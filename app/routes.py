
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required
from datetime import datetime
from . import db
from .models import Competition, Edition, Paper, ChangeLog, SearchRun

public_bp=Blueprint("public",__name__)
api_bp=Blueprint("api",__name__)
admin_bp=Blueprint("admin",__name__)

class AdminUser(UserMixin):
    id="admin"

@public_bp.get("/")
def home():
    return render_template("index.html")

@api_bp.get("/competitions")
def competitions():
    q=request.args.get("q","").strip()
    country=request.args.get("country","")
    status=request.args.get("status","")
    query=Competition.query
    if q:
        like=f"%{q}%"
        query=query.filter(db.or_(Competition.name.ilike(like),Competition.organizer.ilike(like),Competition.target.ilike(like)))
    out=[]
    for c in query.order_by(Competition.name).all():
        for e in c.editions:
            if country and country not in (c.country or ""): continue
            if status and e.status != status: continue
            out.append({
                "id":c.id,"name":c.name,"country":c.country,"organizer":c.organizer,
                "official_url":c.official_url,"description":c.description,
                "year":e.year,"registration_start":e.registration_start.isoformat() if e.registration_start else None,
                "registration_end":e.registration_end.isoformat() if e.registration_end else None,
                "event_date":e.event_date,"fee":e.fee,"target":e.target or c.target,
                "difficulty":e.difficulty,"difficulty_note":e.difficulty_note,"status":e.status,
                "papers":[{"title":p.title,"paper_url":p.paper_url,"solution_url":p.solution_url} for p in e.papers]
            })
    return jsonify(out)

@api_bp.get("/stats")
def stats():
    return jsonify(competitions=Competition.query.count(),editions=Edition.query.count(),papers=Paper.query.count(),
                   open=Edition.query.filter_by(status="open").count(),
                   last_run=(SearchRun.query.order_by(SearchRun.id.desc()).first().finished_at.isoformat() if SearchRun.query.first() and SearchRun.query.order_by(SearchRun.id.desc()).first().finished_at else None))

@api_bp.get("/changes")
def changes():
    rows=ChangeLog.query.order_by(ChangeLog.checked_at.desc()).limit(100).all()
    return jsonify([{"checked_at":r.checked_at.isoformat(),"field":r.field_name,"old":r.old_value,"new":r.new_value,"source":r.source_url} for r in rows])

@admin_bp.get("/login")
def login():
    return render_template("login.html")

@admin_bp.post("/login")
def login_post():
    from flask import current_app
    if request.form.get("email")==current_app.config["ADMIN_EMAIL"] and request.form.get("password")==current_app.config["ADMIN_PASSWORD"]:
        login_user(AdminUser()); return redirect(url_for("admin.dashboard"))
    flash("登入資訊錯誤")
    return redirect(url_for("admin.login"))

@admin_bp.get("/logout")
@login_required
def logout():
    logout_user(); return redirect(url_for("public.home"))

@admin_bp.get("/")
@login_required
def dashboard():
    runs=SearchRun.query.order_by(SearchRun.id.desc()).limit(20).all()
    return render_template("admin.html",runs=runs)

@admin_bp.post("/run")
@login_required
def run_now():
    from worker.updater import run_update
    result=run_update()
    flash(f"更新完成：新增 {result['new']}、更新 {result['updated']}、試題 {result['papers']}、錯誤 {result['errors']}")
    return redirect(url_for("admin.dashboard"))
