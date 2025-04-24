"""
Database models for Stulz HVAC Troubleshooting Application
Defines SQLAlchemy models for the PostgreSQL database
"""
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

# Association table for equipment model relationships
module_compatibility = db.Table('module_compatibility',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('controller_id', db.Integer, db.ForeignKey('equipment_models.id')),
    db.Column('module_id', db.Integer, db.ForeignKey('equipment_models.id')),
    db.Column('compatibility_notes', db.Text),
    db.Column('firmware_requirements', db.String(100)),
    db.Column('max_modules_supported', db.Integer)
)

class EquipmentModel(db.Model):
    """Equipment model database model"""
    __tablename__ = 'equipment_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    model_number = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text)
    ordering_info = db.Column(db.Text, nullable=True)
    
    # Relationships
    specifications = db.relationship('EquipmentSpec', backref='model', lazy='dynamic')
    issues = db.relationship('CommonIssue', backref='model', lazy='dynamic')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'model_number': self.model_number,
            'description': self.description,
            'ordering_info': self.ordering_info
        }


class EquipmentSpec(db.Model):
    """Equipment specification database model"""
    __tablename__ = 'equipment_specs'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('equipment_models.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'model_id': self.model_id,
            'name': self.name,
            'value': self.value
        }


class CommonIssue(db.Model):
    """Common issue database model"""
    __tablename__ = 'common_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('equipment_models.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    troubleshooting_steps = db.relationship('TroubleshootingStep', backref='issue', lazy='dynamic')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'model_id': self.model_id,
            'title': self.title,
            'description': self.description
        }


class TroubleshootingStep(db.Model):
    """Troubleshooting steps database model"""
    __tablename__ = 'troubleshooting_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('common_issues.id'), nullable=False)
    steps = db.Column(db.Text, nullable=False)  # JSON string
    
    def get_steps(self):
        """Get steps as a Python dictionary"""
        return json.loads(self.steps)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'issue_id': self.issue_id,
            'steps': self.get_steps()
        }


class Solution(db.Model):
    """Solution database model"""
    __tablename__ = 'solutions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }


class ReferenceMaterial(db.Model):
    """Reference material database model"""
    __tablename__ = 'reference_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'category': self.category,
            'title': self.title,
            'description': self.description
        }


# Database helper functions
def get_equipment_models():
    """Get all equipment models"""
    models = EquipmentModel.query.all()
    return [model.to_dict() for model in models]

def get_equipment_details(model_id):
    """Get detailed information about a specific equipment model"""
    model = EquipmentModel.query.get(model_id)
    if not model:
        return None
    
    model_dict = model.to_dict()
    specs = EquipmentSpec.query.filter_by(model_id=model_id).all()
    model_dict['specifications'] = [spec.to_dict() for spec in specs]
    
    return model_dict

def get_common_issues(model_id):
    """Get common issues for a specific equipment model"""
    issues = CommonIssue.query.filter_by(model_id=model_id).all()
    return [issue.to_dict() for issue in issues]

def get_troubleshooting_steps(issue_id):
    """Get troubleshooting steps for a specific issue"""
    steps_data = TroubleshootingStep.query.filter_by(issue_id=issue_id).first()
    if not steps_data:
        return None
    
    issue = CommonIssue.query.get(issue_id)
    if not issue:
        return None
    
    return {
        'issue': issue.to_dict(),
        'steps': steps_data.get_steps()
    }

def get_solutions(issue_id):
    """Get solutions for a specific issue"""
    steps_data = TroubleshootingStep.query.filter_by(issue_id=issue_id).first()
    if not steps_data:
        return {"solutions": []}
    
    # Parse the steps to find solution IDs
    steps = steps_data.get_steps()
    
    # Extract all solution IDs from the steps
    solution_ids = []
    for node_key, node in steps.items():
        if "solution" in node:
            solution_id = node["solution"] if isinstance(node["solution"], int) else None
            if solution_id and solution_id not in solution_ids:
                solution_ids.append(solution_id)
    
    # Get solution details for all solution IDs
    solutions = []
    for solution_id in solution_ids:
        solution_data = Solution.query.get(solution_id)
        if solution_data:
            solutions.append(solution_data.to_dict())
    
    return {"solutions": solutions}

def search_equipment_by_model_number(model_number):
    """Search for equipment models by model number"""
    models = EquipmentModel.query.filter(
        EquipmentModel.model_number.ilike(f'%{model_number}%')
    ).all()
    
    return [model.to_dict() for model in models]

def search_issues(query):
    """Search for issues and solutions based on keyword"""
    # Search in issues
    issues = CommonIssue.query.filter(
        (CommonIssue.title.ilike(f'%{query}%')) | 
        (CommonIssue.description.ilike(f'%{query}%'))
    ).all()
    
    # Get equipment model names for issues
    issue_results = []
    for issue in issues:
        issue_dict = issue.to_dict()
        model = EquipmentModel.query.get(issue.model_id)
        if model:
            issue_dict['equipment_model'] = model.name
        issue_results.append(issue_dict)
    
    # Search in solutions
    solutions = Solution.query.filter(
        (Solution.title.ilike(f'%{query}%')) | 
        (Solution.description.ilike(f'%{query}%'))
    ).all()
    
    return {
        "issues": issue_results,
        "solutions": [solution.to_dict() for solution in solutions]
    }

def get_reference_materials(category=None):
    """Get reference materials, optionally filtered by category"""
    if category:
        materials = ReferenceMaterial.query.filter_by(category=category).all()
    else:
        materials = ReferenceMaterial.query.all()
    
    # Get unique categories for filtering
    categories = db.session.query(ReferenceMaterial.category).distinct().all()
    
    return {
        "materials": [material.to_dict() for material in materials],
        "categories": [cat[0] for cat in categories]
    }


def get_compatible_modules(controller_id):
    """Get modules compatible with a specific controller"""
    # Query the module_compatibility table for this controller
    compatibility_data = db.session.execute(
        module_compatibility.select().where(module_compatibility.c.controller_id == controller_id)
    ).fetchall()
    
    if not compatibility_data:
        return {"compatible_modules": []}
    
    result = {"compatible_modules": []}
    for comp in compatibility_data:
        # Get module details
        module = EquipmentModel.query.get(comp.module_id)
        if module:
            module_dict = module.to_dict()
            # Add compatibility details
            module_dict["compatibility_notes"] = comp.compatibility_notes
            module_dict["firmware_requirements"] = comp.firmware_requirements
            module_dict["max_modules_supported"] = comp.max_modules_supported
            result["compatible_modules"].append(module_dict)
    
    return result


def get_module_compatibility(module_id):
    """Get list of controllers compatible with a specific module"""
    # Query the module_compatibility table for this module
    compatibility_data = db.session.execute(
        module_compatibility.select().where(module_compatibility.c.module_id == module_id)
    ).fetchall()
    
    if not compatibility_data:
        return {"compatible_controllers": []}
    
    result = {"compatible_controllers": []}
    for comp in compatibility_data:
        # Get controller details
        controller = EquipmentModel.query.get(comp.controller_id)
        if controller:
            controller_dict = controller.to_dict()
            # Add compatibility details
            controller_dict["compatibility_notes"] = comp.compatibility_notes
            controller_dict["firmware_requirements"] = comp.firmware_requirements
            controller_dict["max_modules_supported"] = comp.max_modules_supported
            result["compatible_controllers"].append(controller_dict)
    
    return result