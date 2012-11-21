## This file is part of Invenio.
## Copyright (C) 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Holding Pen & BibWorkflow web interface"""

__revision__ = "$Id$"

__lastupdated__ = """$Date$"""

from flask import Flask, render_template, redirect, url_for, Markup
from invenio.bibworkflow_model import Workflow, WfeObject
from invenio.bibworkflow_api import run
import os
from sqlalchemy import or_
from invenio.sqlalchemyutils import db
from invenio.pluginutils import PluginContainer
from invenio.config import CFG_SITE_SECURE_URL, CFG_SITE_URL, CFG_ACCESS_CONTROL_LEVEL_SITE, CFG_PYLIBDIR, CFG_LOGDIR
from invenio.urlutils import redirect_to_url
from invenio.webinterface_handler_flask_utils import _, InvenioBlueprint
from invenio.bibworkflow_utils import getWorkflowDefinition

import traceback

blueprint = InvenioBlueprint('bibworkflow', __name__, url_prefix="/admin/bibworkflow",
            menubuilder=[('main.admin.bibworkflow', _('BibWorkflow'),
                          'bibworkflow.index')],
            breadcrumbs=[(_('Administration'),'help.admin'),
                         (_('BibWorkflow'),'bibworkflow.index')],)

#@app.route("/")
@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/index', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_templated('bibworkflow_index.html')
def index():
    """
    Dispalys main interface of BibWorkflow.
    """
    w = Workflow.query.all()
    return dict(workflows=w)

@blueprint.route('/entry_details', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'entry_id': (int, 0)})
def entry_details(entry_id):
    """
    Dispalys entry details.
    """
    object = WfeObject.query.filter(WfeObject.id == entry_id).first()
    try:
        #object_210_w_18
        f = open(CFG_LOGDIR + "/object_"+ str(object.id) + "_w_" + str(object.workflow_id) + ".log", "r")
        logtext = f.read()
    except IOError, e:
        # no file
        logtext = "" 
 
    return render_template('bibworkflow_entry_details.html', entry=object, log=logtext, data_preview=_entry_data_preview(object.data,'hd'), workflow_func=getWorkflowDefinition(object.bwlWORKFLOW.name))

@blueprint.route('/workflow_details', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'workflow_id': (unicode, "")})
def workflow_details(workflow_id):
    w_metadata = Workflow.query.filter(Workflow.uuid == workflow_id).first()

    try:
        f = open(CFG_LOGDIR + "/workflow_" + str(workflow_id) + ".log", "r")
        logtext = f.read()
    except IOError, e:
        # no file
        logtext = ""

    return render_template('bibworkflow_workflow_details.html', workflow_metadata=w_metadata, log=logtext, workflow_func=getWorkflowDefinition(w_metadata.name))

@blueprint.route('/workflows', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_templated('bibworkflow_workflows.html')
def workflows():
    try:
        workflows = PluginContainer(os.path.join(CFG_PYLIBDIR, 'invenio', 'bibworkflow', 'workflows', '*.py'))
        print workflows.get_broken_plugins()
    except:
        traceback.print_exc()
    return dict(workflows=workflows.get_enabled_plugins(),broken_workflows=workflows.get_broken_plugins())

@blueprint.route('/run_workflow', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'workflow_name': (unicode, "")})
def run_workflow(workflow_name):
    try:
        #data = [{'596':120},{'a': 'bbb'},{'a': 20},{'a': 50},{'a': 100},{'a': 'aa'}]
        data = [{'a': 3}, {'b': 4}]
        run(workflow_name, data)
    except:
        traceback.print_exc()
    return "Workflow has been started."
    
@blueprint.route('/entry_data_preview', methods=['GET', 'POST'])
@blueprint.invenio_authenticated
@blueprint.invenio_wash_urlargd({'oid': (int, 0), 'format': (unicode, 'default')})
def entry_data_preview(oid, format):
    object = WfeObject.query.filter(WfeObject.id == oid).first()
    return _entry_data_preview(object.data,format)
    

def _entry_data_preview(data,format='default'):
    if format == 'hd' or format == 'xm':
        from invenio.bibformat import format_record
        try:
            data['record'] = format_record(recID = None, of = format, xml_record = data['record'])
        except:
            print "This is not a XML string"
    try:
        return data['record']
    except:
        return data
