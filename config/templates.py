routes_file_template = """from datetime import datetime
from flask import jsonify, request, g, abort
from flask_babel import _
from flasgger import swag_from

from api.v1.routes import app_routes
from api.v1.schemas import json_validate
from api.v1.schemas.{section} import (
    {schemas}
)
from models import storage, {tags}
from models.base import time_fmt
from models.engine.relational_storage import paginate

{routes}"""


route_template = """
@app_routes.route("{route_path}", methods=["{method}"], strict_slashes=False)
@swag_from('documentation/{section}/{route_handler}.yml')
def {route_handler}({params}):
    \"\"\"{method} {path}
    Return:
      - on success: {desc}
      - on error: respond with {errors} error codes
    \"\"\"
    req = dict(request.args)
    if request.content_type == 'application/json':
        req.update(request.json)
    SCHEMA = {route_handler_upper}_SCHEMA
    error_response = json_validate(req, SCHEMA)
    if error_response is not None:
        return error_response
"""

schema_template = """\"\"\"JSON request validation schemas for the {section} endpoints
\"\"\"

{schemas}"""

routes_import_template = """\"\"\" API Routes
\"\"\"
from flask import Blueprint

app_routes = Blueprint("app_views", __name__, url_prefix="/api/v1")

{routes_import}
"""

model_template = """from sqlalchemy import Column, ForeignKey, {imported_types}
from sqlalchemy.orm import relationship
from models.base import BaseModel, Base
{imported_models}

class {class_name}(Base, BaseModel):
    \"\"\"{class_name} DB model class
    \"\"\"
    __tablename__ = '{table_name}'

    def __init__(self, {ctor_args}**kwargs):
        \"\"\"initialize a {class_name} instance
        \"\"\"
        kwargs.update({attrs})
        super().__init__(**kwargs) 

{columns}
{deffered_rels}
"""

models_import_template = """from models.engine.relational_storage import RelationalStorage
{models_import}
from bcrypt import hashpw, gensalt

classes = {{{classes}}}

storage = RelationalStorage()
storage.reload()

if storage.query(User).where(User.user_name == 'admin').one_or_none() is None:
	admin = storage.new(User(email='admin@quizquickie.com', password=hashpw('admin'.encode(), gensalt()), user_name='admin')).save()
"""

assoc_table_template = """
from sqlalchemy import Table, Column, ForeignKey, {imported_types}
from models.base import Base

{table_name} = Table('{table_name}', Base.metadata,
    {attrs}
)"""
