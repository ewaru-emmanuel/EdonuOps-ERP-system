from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    # Fix ambiguity: specify which FK to use
    organization = db.relationship(
        'Organization',
        foreign_keys=[organization_id],
        backref=db.backref('members', lazy=True)
    )

class Organization(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Add explicit relationship back to the user who created the organization
    creator = db.relationship(
        'User',
        foreign_keys=[created_by_user_id],
        backref='created_organizations'
    )

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.JSON)
