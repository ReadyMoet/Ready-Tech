"""
Ready Tech - Flask Backend
This module serves as the backend for Ready Tech,
providing API endpoints and serving the frontend for commercial HVAC troubleshooting.
"""
import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from config import config
from models_new import (
    db,
    get_equipment_models,
    get_equipment_details,
    get_common_issues,
    get_troubleshooting_steps,
    get_solutions,
    search_issues,
    search_equipment_by_model_number,
    get_reference_materials,
    get_compatible_modules,
    get_module_compatibility
)
from openai import OpenAI

# Create Flask application
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/equipment')
def equipment():
    """Render the equipment selection page"""
    return render_template('equipment.html')

@app.route('/troubleshooting')
def troubleshooting():
    """Render the troubleshooting workflow page"""
    return render_template('troubleshooting.html')

@app.route('/solutions')
def solutions():
    """Render the solutions page"""
    return render_template('solutions.html')

@app.route('/reference')
def reference():
    """Render the reference materials page"""
    return render_template('reference.html')

@app.route('/buddy')
def buddy():
    """Render the Tech Assistant page"""
    return render_template('buddy.html')

@app.route('/tests')
def tests():
    """Render the issues testing page"""
    return render_template('issues-test.html')

@app.route('/qa')
def qa():
    """Render the Problem Solver page for HVAC troubleshooting"""
    return render_template('qa.html')

@app.route('/api/equipment/models', methods=['GET'])
def api_equipment_models():
    """Return all available equipment models"""
    try:
        models = get_equipment_models()
        return jsonify(models)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/equipment/<int:model_id>', methods=['GET'])
def api_equipment_details(model_id):
    """Return details for specific equipment model"""
    try:
        details = get_equipment_details(model_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/issues/<int:model_id>', methods=['GET'])
def api_common_issues(model_id):
    """Return common issues for specific equipment model"""
    try:
        issues = get_common_issues(model_id)
        return jsonify(issues)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/troubleshooting/<int:issue_id>', methods=['GET'])
def api_troubleshooting_steps(issue_id):
    """Return troubleshooting steps for a specific issue"""
    try:
        steps = get_troubleshooting_steps(issue_id)
        return jsonify(steps)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/solutions/<int:issue_id>', methods=['GET'])
def api_solutions(issue_id):
    """Return solutions for a specific issue"""
    try:
        solutions_data = get_solutions(issue_id)
        return jsonify(solutions_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/equipment/search/model_number', methods=['GET'])
def api_search_equipment_by_model_number():
    """Search for equipment by model number"""
    model_number = request.args.get('query', '')
    if not model_number:
        return jsonify({"error": "No search query provided"}), 400
    
    try:
        results = search_equipment_by_model_number(model_number)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def api_search():
    """Search issues and solutions"""
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    try:
        results = search_issues(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reference', methods=['GET'])
def api_reference():
    """Return reference materials"""
    category = request.args.get('category', None)
    try:
        materials = get_reference_materials(category)
        return jsonify(materials)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compatibility/modules/<int:controller_id>', methods=['GET'])
def api_compatible_modules(controller_id):
    """Return modules compatible with a specific controller"""
    try:
        modules = get_compatible_modules(controller_id)
        return jsonify(modules)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compatibility/controllers/<int:module_id>', methods=['GET'])
def api_module_compatibility(module_id):
    """Return controllers compatible with a specific module"""
    try:
        controllers = get_module_compatibility(module_id)
        return jsonify(controllers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tests/issues', methods=['GET'])
def api_test_issues():
    """Return the list of test issues for automated testing"""
    test_issues = [
        {
            "id": "test-1",
            "title": "Compressor Won't Start",
            "description": "Unit is powered but compressor does not start when called for cooling"
        },
        {
            "id": "test-2",
            "title": "Fan Motor Not Running",
            "description": "Supply fan not operating despite controller showing fan command"
        },
        {
            "id": "test-3",
            "title": "High Head Pressure Alarm",
            "description": "System showing high discharge pressure readings and triggering alarms"
        },
        {
            "id": "test-4",
            "title": "Communication Error with BMS",
            "description": "Building management system shows controller offline or communication failure"
        },
        {
            "id": "test-5",
            "title": "Low Suction Pressure",
            "description": "Evaporator has low refrigerant pressure, causing reduced cooling capacity"
        }
    ]
    return jsonify(test_issues)

@app.route('/api/qa/answer', methods=['POST'])
def api_qa_answer():
    """Get solution from OpenAI API for HVAC problems"""
    try:
        data = request.get_json()
        if not data:
            print("No JSON data received in request")
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        if 'problem' not in data and 'question' not in data:
            print("No problem or question found in request data")
            return jsonify({"status": "error", "message": "No problem provided"}), 400
        
        problem = data.get('problem', data.get('question', ''))
        include_context = data.get('include_context', True)
        manufacturer = data.get('manufacturer', '')
        model_series = data.get('model_series', '')
        ai_model = data.get('ai_model', 'openai')  # We're only using OpenAI, but keeping the parameter for compatibility
        
        print(f"Received problem: '{problem[:50]}...' (truncated)")
        print(f"Include context: {include_context}")
        print(f"Manufacturer: {manufacturer if manufacturer else 'Not specified'}")
        print(f"Model Series: {model_series if model_series else 'Not specified'}")
        print(f"AI Model: {ai_model}")
        
        # Define system message with HVAC knowledge
        system_message = """
        You are an expert HVAC technician specializing in commercial refrigeration systems and building controls.
        Provide detailed, technically accurate solutions to HVAC problems with a focus on practical troubleshooting, 
        diagnostic steps, and repair procedures. Treat all user input as problem descriptions, not questions.
        
        For each problem:
        1. First identify the likely cause(s) based on the symptoms described
        2. Provide step-by-step diagnostic procedures to confirm the issue
        3. Explain repair or resolution steps in a detailed, actionable format
        4. Include specific measurements, safety precautions, and industry best practices
        
        Prioritize practical information that would be useful to field technicians working on HVAC systems.
        Answer in a clear, organized manner using short paragraphs, numbered steps, bullet points, and technical terminology.
        """
        
        # Add manufacturer-specific guidance if provided
        if manufacturer:
            if manufacturer == "Stulz":
                system_message += """
                Focus specifically on Stulz HVAC systems, which specialize in precision cooling for data centers and mission-critical facilities.
                Include information about:
                - Stulz controllers like pCO5 (basic) and pCO5+ (enhanced with expanded I/O and connectivity)
                - BMS connectivity options including ModBus, BACnet, and LonWorks protocols
                - Typical configurations of Stulz precision cooling units
                - Common alarm codes and their resolution procedures for Stulz equipment
                """
                
                # Add model series-specific information if provided
                if model_series:
                    if "CyberAir" in model_series:
                        system_message += """
                        Focus on Stulz CyberAir units, which are precision downflow cooling systems designed for large data centers:
                        - High capacity units (20-140kW cooling capacity)
                        - Available with EC fans for energy efficiency
                        - Multiple refrigerant circuit options
                        - Intelligent free cooling modes (CW2, DX2, GE) to save energy
                        - Common issues include EC fan failures, EEV malfunctions, and communication errors with pCO controllers
                        """
                    elif "MiniSpace" in model_series:
                        system_message += """
                        Focus on Stulz MiniSpace units, which are compact precision cooling systems:
                        - Smaller capacity (6-28kW)
                        - Designed for IT closets, small server rooms, and telecom enclosures
                        - Available in upflow or downflow configurations
                        - Common issues include condensate pump failures, compressor cycling, and filter clogging
                        """
                    elif "CyberRow" in model_series:
                        system_message += """
                        Focus on Stulz CyberRow units, which are in-row cooling solutions:
                        - Designed to be placed directly between server racks
                        - Horizontal airflow for more efficient cooling in high-density environments
                        - Available in chilled water and DX versions
                        - Common issues include control valve failures, condensate management problems, and airflow distribution issues
                        """
                    elif "WallAir" in model_series:
                        system_message += """
                        Focus on Stulz WallAir units, which are wall-mounted precision cooling systems:
                        - Designed for telecom shelters, small equipment rooms, and edge computing
                        - Available in DX and free cooling configurations
                        - Typically includes integrated free cooling options
                        - Common issues include outdoor coil fouling, refrigerant circuit problems in extreme weather, and control system lockups
                        """
            elif manufacturer == "Vertiv":
                system_message += """
                Focus specifically on Vertiv (formerly Emerson Network Power) HVAC systems, particularly their Liebert product line.
                Include information about:
                - Liebert iCOM and iCOM-S controller systems and their common issues
                - Vertiv's Thermal Management products including Liebert CRV, PDX/PCW, and DS/CW
                - Liebert MC microchannel condensers and their specific requirements
                - Addressing Vertiv-specific error codes and alarm procedures
                """
                
                # Add model series-specific information if provided
                if model_series:
                    if "Liebert CRV" in model_series:
                        system_message += """
                        Focus on Liebert CRV units, which are in-row cooling solutions:
                        - Designed for targeted cooling in data centers with hot/cold aisle configurations
                        - Available in 20-35kW capacities
                        - Variable capacity digital scroll compressors and EC fans for precise temperature control
                        - Common issues include refrigerant loss, iCOM controller errors, and EC fan motor failures
                        - Diagnosis often requires checking Liebert iCOM fault logs and parameter settings
                        """
                    elif "Liebert PDX/PCW" in model_series:
                        system_message += """
                        Focus on Liebert PDX/PCW units:
                        - PDX: Direct Expansion (refrigerant-based) cooling
                        - PCW: Chilled water cooling
                        - Available in downflow and upflow configurations (20-240kW)
                        - Liebert iCOM control systems with touchscreen interface
                        - Common issues include high head pressure, water leakage from chilled water valve failures,
                          compressor overheating, and communication errors with BMS systems
                        """
                    elif "Liebert DS/CW" in model_series:
                        system_message += """
                        Focus on Liebert DS/CW units:
                        - High-capacity precision cooling (35-105kW)
                        - DS: Direct Expansion refrigerant-based cooling
                        - CW: Chilled water cooling
                        - Features dual-circuit design for redundancy
                        - Common issues include refrigerant leaks, condenser fan motor failures,
                          valve failures in chilled water systems, and control system errors
                        - Critical to check superheat and subcooling values when diagnosing refrigeration issues
                        """
                    elif "Liebert DSE" in model_series:
                        system_message += """
                        Focus on Liebert DSE units:
                        - High-efficiency precision cooling using EconoPhase pumped refrigerant technology
                        - Available in 50-165kW capacities
                        - Features free-cooling capability using pumped refrigerant economizer
                        - CRAC systems with integrated economization
                        - Common issues include pumped refrigerant circuit problems, refrigerant migration,
                          EEV failures, and Liebert iCOM control communication errors
                        - Often requires special attention to economizer transition settings
                        """
            elif manufacturer == "Schneider":
                system_message += """
                Focus specifically on Schneider Electric cooling solutions, particularly for data center environments.
                Include information about:
                - InRow cooling solutions and their integration with hot/cold aisle containment
                - StruxureWare monitoring and control systems
                - NetBotz room monitoring systems when relevant
                - EcoBreeze and EcoAisle technologies for free cooling applications
                """
            elif manufacturer == "DataAire":
                system_message += """
                Focus specifically on DataAire precision cooling systems, which are designed for data centers and tech environments.
                Include information about:
                - gForce Series floor-mounted and ceiling-mounted precision cooling units
                - dap4 microprocessor controllers and their programming interfaces
                - Mini-dap controllers for smaller systems
                - DataAire's gPod modular cooling solutions
                """
            elif manufacturer == "Munters":
                system_message += """
                Focus specifically on Munters air treatment systems, which specialize in humidity control and energy-efficient cooling.
                Include information about:
                - Desiccant dehumidification systems and their regeneration cycles
                - Oasis Indirect Evaporative Cooling technology
                - Munters DryCool systems that combine desiccant drying with conventional cooling
                - HCU (Heat recovery/Cooling units) control systems
                """
            else:
                # Generic manufacturer-specific guidance for other brands
                system_message += f"""
                Focus specifically on {manufacturer} HVAC equipment and their typical system configurations.
                Include information about their control systems, common error codes, and recommended troubleshooting
                procedures where applicable.
                """
        else:
            # Default to Stulz if no manufacturer is specified (maintaining backward compatibility)
            system_message += """
            Focus particularly on Stulz HVAC systems, controllers like pCO5 and pCO5+, and commercial cooling systems.
            """
        
        # Add context if requested
        if include_context:
            # Add specific information about HVAC systems relevant to the app
            system_message += """
            Special considerations for various controller types:
            - pCO5: Standard controller with basic BMS protocols (Modbus, BACnet)
            - pCO5+: Enhanced controller with expanded I/O and connectivity options
            
            Common refrigerants: R-134a, R-410A, R-407C, R-32.
            Key heat rejection systems: Air-Cooled Condensers, Dry Coolers, Cooling Towers, Adiabatic Coolers, Fluid Coolers.
            
            When troubleshooting:
            1. Verify proper voltage and phasing first
            2. Check refrigerant pressures and temperatures
            3. Examine controller parameters and alarm history
            4. Inspect mechanical components for visible damage
            5. Analyze superheat and subcooling values
            
            Winter operation requires special attention to:
            - Head pressure control setup
            - Defrost cycle programming
            - Wind baffle positioning
            - Glycol concentration levels
            - Heat trace functionality
            """
        
        # Get OpenAI API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("No OpenAI API key found in environment variables")
            return jsonify({"status": "error", "message": "OpenAI API key not configured"}), 500
        
        print("API key found, initializing OpenAI client")
        
        # Initialize OpenAI client
        try:
            client = OpenAI(api_key=api_key)
            print("OpenAI client initialized successfully")
        except Exception as client_err:
            print(f"Error initializing OpenAI client: {str(client_err)}")
            return jsonify({
                "status": "error", 
                "message": f"Failed to initialize OpenAI client: {str(client_err)}"
            }), 500
        
        # Make API request to OpenAI
        try:
            print("Sending request to OpenAI API...")
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": problem}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            print("Successfully received response from OpenAI API")
            
            # Extract the answer from the response
            answer = response.choices[0].message.content
            
            print(f"Answer: '{answer[:50]}...' (truncated)")
            
            # Return the answer
            return jsonify({
                "status": "success",
                "answer": answer,
                "citations": [],  # OpenAI doesn't provide citations by default
                "model_used": "OpenAI GPT-4o"
            })
            
        except Exception as api_error:
            print(f"OpenAI API request failed: {str(api_error)}")
            error_message = f"OpenAI API request failed: {str(api_error)}"
            
            # Check if this is a quota error
            if 'insufficient_quota' in str(api_error) or 'exceeded your current quota' in str(api_error):
                print("Providing fallback response due to quota limitation")
                
                # Provide a helpful fallback response
                fallback_response = """
                # HVAC Troubleshooting Guide
                
                ## Common Diagnostic Steps
                
                When troubleshooting HVAC issues, follow these general steps:
                
                1. **Verify power supply and electrical connections**
                   - Check circuit breakers, fuses, and disconnects
                   - Measure voltage at equipment terminals
                   - Inspect wiring for damage or loose connections
                
                2. **Check control systems**
                   - Verify thermostat/controller settings and operation
                   - Test control signals and communication networks
                   - Check for error codes on digital displays
                
                3. **Inspect mechanical components**
                   - Look for visible damage, unusual wear, or debris
                   - Listen for abnormal sounds during operation
                   - Check for proper mechanical movement
                
                4. **Monitor refrigeration system (if applicable)**
                   - Measure refrigerant pressures and temperatures
                   - Calculate superheat and subcooling values
                   - Check for refrigerant leaks
                
                5. **Evaluate airflow or water flow**
                   - Verify proper fan or pump operation
                   - Check for restrictions or blockages
                   - Measure flow rates if equipment is available
                
                ## Documentation
                
                For specific troubleshooting steps for your equipment:
                
                - Consult the manufacturer's service manual
                - Check technical bulletins for known issues
                - Reference industry standards for proper measurements
                
                *Note: This is general guidance. Please consult equipment-specific documentation for detailed procedures.*
                """
                
                return jsonify({
                    "status": "success",
                    "answer": fallback_response,
                    "citations": [],
                    "model_used": "Fallback Guide"
                })
            else:
                # For other types of errors, return the error message
                return jsonify({
                    "status": "error", 
                    "message": error_message
                }), 500
    
    except Exception as e:
        print(f"Unexpected error in api_qa_answer: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Failed to get answer: {str(e)}"
        }), 500

@app.route('/api/database/migrate', methods=['GET'])
def api_db_migrate():
    """Run database migration (for development only)"""
    try:
        # Import here to avoid circular imports
        from migrations import init_db
        init_db()
        return jsonify({"status": "success", "message": "Database migration completed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Add current date to template context
@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.utcnow()}

# Serve the PWA service worker file
@app.route('/service-worker.js')
def serve_service_worker():
    return app.send_static_file('js/service-worker.js')

if __name__ == '__main__':
    # For development only - Electron will handle the production serving
    app.run(host='0.0.0.0', port=5000, debug=True)