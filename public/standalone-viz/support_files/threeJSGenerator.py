def generate_direct_shape_js(safe_variable2, shape_mapping_js):
    """
    Generate JavaScript code that directly manipulates THREE.js objects in Emperor
    to replace point geometries with custom 3D shapes.
    
    Args:
        safe_variable2 (str): The JavaScript-safe escaped variable2 name
        shape_mapping_js (str): JavaScript object string mapping variable values to shapes
    
    Returns:
        str: JavaScript code for shape manipulation
    """
    
    direct_shape_js = f"""// This script directly manipulates the THREE.js objects in Emperor
        // Map of shape names to THREE.js geometry creation functions
        const SHAPE_GEOMETRIES = {{
        'Cone': function() {{
            return new THREE.ConeGeometry(0.5, 1, 8);
        }},
        'Sphere': function() {{
            return new THREE.SphereGeometry(0.5, 16, 16);
        }},
        'Star': function() {{
            // Create a star shape
            const starShape = new THREE.Shape();
            const outerRadius = 0.5;
            const innerRadius = 0.2;
            const spikes = 5;
            
            for (let i = 0; i < spikes * 2; i++) {{
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const angle = (Math.PI * 2 * i) / (spikes * 2);
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            
            if (i === 0) {{
                starShape.moveTo(x, y);
            }} else {{
                starShape.lineTo(x, y);
            }}
            }}
            starShape.closePath();
            
            const extrudeSettings = {{
            depth: 0.2,
            bevelEnabled: false
            }};
            
            return new THREE.ExtrudeGeometry(starShape, extrudeSettings);
        }},
        'Cylinder': function() {{
            return new THREE.CylinderGeometry(0.4, 0.4, 0.8, 16);
        }},
        'Box': function() {{
            return new THREE.BoxGeometry(0.8, 0.8, 0.8);
        }},
        'Octahedron': function() {{
            return new THREE.OctahedronGeometry(0.5);
        }},
        'Tetrahedron': function() {{
            return new THREE.TetrahedronGeometry(0.6);
        }},
        'Torus': function() {{
            return new THREE.TorusGeometry(0.4, 0.2, 8, 16);
        }},
        'Diamond': function() {{
            return new THREE.OctahedronGeometry(0.5);
        }},
        'Ring': function() {{
            return new THREE.TorusGeometry(0.4, 0.1, 8, 16);
        }},
        'Icosahedron': function() {{
            return new THREE.IcosahedronGeometry(0.5);
        }},
        'Square': function() {{
            return new THREE.BoxGeometry(0.8, 0.8, 0.2);
        }}
        }};

        // Function to directly replace geometries in THREE.js scene
        function replaceGeometries() {{
        // Accessing Emperor's controller
        if (typeof empObj === 'undefined' || !empObj.sceneViews || !empObj.sceneViews[0]) {{
            console.log("Emperor or scene view not available yet");
            return false;
        }}
        
        const sceneView = empObj.sceneViews[0];
        const scene = sceneView.scene;
        const metadata = window.data.plot.metadata;
        const metadataHeaders = window.data.plot.metadata_headers;
        
        // Find variable2 index in metadata
        let variable2Index = -1;
        for (let i = 0; i < metadataHeaders.length; i++) {{
            if (metadataHeaders[i] === {safe_variable2}) {{
            variable2Index = i;
            break;
            }}
        }}
        
        if (variable2Index === -1) {{
            console.log("Variable2 field not found in metadata");
            return false;
        }}
        
        // Create a map from sample ID to variable2 value
        const sampleToVariable2 = {{}};
        for (const sampleId in metadata) {{
            if (metadata.hasOwnProperty(sampleId)) {{
            sampleToVariable2[sampleId] = metadata[sampleId][variable2Index];
            }}
        }}
        
        // Map variable2 values to shape types - DYNAMIC MAPPING
        const variable2ToShape = {shape_mapping_js};
        
        // Go through all objects in the scene
        let pointsReplaced = false;
        
        try {{
            // First, try to replace THREE.Points with individual meshes
            for (let i = 0; i < scene.children.length; i++) {{
            const child = scene.children[i];
            
            if (child instanceof THREE.Points) {{
                console.log("Found points object:", child);
                
                // Get the positions from the points
                const positions = child.geometry.attributes.position.array;
                const colors = child.geometry.attributes.color.array;
                const count = child.geometry.attributes.position.count;
                
                // Create a parent object to hold our meshes
                const meshesParent = new THREE.Object3D();
                meshesParent.name = "CustomShapesContainer";
                
                // Get sample IDs if available
                let sampleIds = [];
                if (sceneView.decomp && sceneView.decomp.plottable && sceneView.decomp.plottable.sample_ids) {{
                sampleIds = sceneView.decomp.plottable.sample_ids;
                }}
                
                // Replace points with appropriate geometries
                for (let j = 0; j < count; j++) {{
                const x = positions[j * 3];
                const y = positions[j * 3 + 1];
                const z = positions[j * 3 + 2];
                
                const r = colors[j * 3];
                const g = colors[j * 3 + 1];
                const b = colors[j * 3 + 2];
                
                // Determine which shape to use based on sample ID and variable2
                let shapeName = 'Sphere'; // Default
                
                if (j < sampleIds.length) {{
                    const sampleId = sampleIds[j];
                    const variable2Value = sampleToVariable2[sampleId];
                    
                    if (variable2Value && variable2ToShape[variable2Value]) {{
                    shapeName = variable2ToShape[variable2Value];
                    }}
                }}
                
                // Create geometry based on shape type
                const geometryFunc = SHAPE_GEOMETRIES[shapeName];
                if (!geometryFunc) continue;
                
                const geometry = geometryFunc();
                const material = new THREE.MeshBasicMaterial({{
                    color: new THREE.Color(r, g, b),
                    transparent: true,
                    opacity: 0.8
                }});
                
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(x, y, z);
                mesh.scale.set(0.3, 0.3, 0.3); // Adjust size as needed
                
                meshesParent.add(mesh);
                }}
                
                // Add the new meshes and remove (or hide) the original points
                scene.add(meshesParent);
                child.visible = false; // Hide instead of remove to preserve original data
                
                pointsReplaced = true;
                console.log(`Replaced ${{count}} points with custom geometries`);
            }}
            }}
            
            // Force a redraw
            if (sceneView.needsUpdate !== undefined) {{
            sceneView.needsUpdate = true;
            }}
            
            // Also try to trigger Emperor's render function
            if (empObj.drawFrame) {{
            empObj.drawFrame();
            }}
            
            return pointsReplaced;
        }} catch (e) {{
            console.error("Error replacing geometries:", e);
            return false;
        }}
        }}

        // Initialize after page load
        document.addEventListener('DOMContentLoaded', function() {{
        console.log("Direct THREE.js shape override script loaded");
        
        // Wait for Emperor to fully initialize
        let attempts = 0;
        const maxAttempts = 20;
        
        function tryReplaceGeometries() {{
            attempts++;
            console.log(`Attempt ${{attempts}} to replace geometries`);
            
            const success = replaceGeometries();
            
            if (success) {{
            console.log("Successfully replaced geometries!");
            }} else if (attempts < maxAttempts) {{
            // Try again after a delay
            setTimeout(tryReplaceGeometries, 1000);
            }} else {{
            console.log(`Failed to replace geometries after ${{maxAttempts}} attempts`);
            }}
        }}
        
        // Start first attempt after 3 seconds to ensure Emperor is fully loaded
        setTimeout(tryReplaceGeometries, 3000);
        }});
        """
    
    return direct_shape_js