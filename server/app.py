#!/usr/bin/env python3
from flask import Flask, request, jsonify, session
from flask_restful import Resource, Api
from models import db, User, Article

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "super-secret-key"

db.init_app(app)


# ------------------------
# Utility route (tests use this)
# ------------------------
@app.route("/clear")
def clear():
    session.clear()
    return {}, 204


# ------------------------
# AUTHENTICATION
# ------------------------
class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get("username")).first()

        if not user:
            return {"error": "User not found"}, 404

        session["user_id"] = user.id
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")

        if not user_id:
            return {}, 401

        user = db.session.get(User, user_id)
        return user.to_dict(), 200


# ------------------------
# AUTHORIZATION (MEMBERS ONLY)
# ------------------------
class MemberOnlyIndex(Resource):
    def get(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        articles = Article.query.filter_by(is_member_only=True).all()
        return [article.to_dict() for article in articles], 200


class MemberOnlyArticle(Resource):
    def get(self, id):
        if not session.get("user_id"):
            return {"error": "Unauthorized"}, 401

        article = db.session.get(Article, id)

        if not article:
            return {"error": "Article not found"}, 404

        return article.to_dict(), 200



# ------------------------
# ROUTES
# ------------------------
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

api.add_resource(MemberOnlyIndex, "/members_only_articles")
api.add_resource(MemberOnlyArticle, "/members_only_articles/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
