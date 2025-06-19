from flask import Blueprint, render_template
from models import db, Course, Instructor, Student, TimeSlot

conflicts_bp = Blueprint('conflicts', __name__)

@conflicts_bp.route('/conflicts')
def view_conflicts():
    # Find student conflicts (students enrolled in courses with same time slot)
    student_conflicts = []
    
    # Courses with assigned time slots
    scheduled_courses = Course.query.filter(Course.time_slot_id.isnot(None)).all()
    
    # Check each student
    students = Student.query.all()
    for student in students:
        # Get student's scheduled courses
        student_courses = [c for c in student.courses if c.time_slot_id is not None]
        
        # Check each pair of courses for time conflicts
        for i in range(len(student_courses)):
            for j in range(i + 1, len(student_courses)):
                course1 = student_courses[i]
                course2 = student_courses[j]
                
                # Get timeslots
                time1 = TimeSlot.query.get(course1.time_slot_id)
                time2 = TimeSlot.query.get(course2.time_slot_id)
                
                # Check if timeslots overlap
                if time1 and time2 and time1.day == time2.day:
                    # Convert times to comparable format
                    start1 = time1.start_time
                    end1 = time1.end_time
                    start2 = time2.start_time
                    end2 = time2.end_time
                    
                    # Check for overlap
                    if (start1 <= start2 < end1) or (start1 < end2 <= end1) or (start2 <= start1 < end2):
                        student_conflicts.append({
                            'student': student,
                            'time_slot1': time1,
                            'time_slot2': time2,
                            'courses': [course1, course2]
                        })
    
    # Find instructor conflicts (instructor assigned to multiple courses in same time slot)
    instructor_conflicts = []
    instructors = Instructor.query.all()
    
    for instructor in instructors:
        # Get instructor's scheduled courses
        instructor_courses = Course.query.filter(
            Course.instructor_id == instructor.id,
            Course.time_slot_id.isnot(None)
        ).all()
        
        # Check each pair of courses for time conflicts
        for i in range(len(instructor_courses)):
            for j in range(i + 1, len(instructor_courses)):
                course1 = instructor_courses[i]
                course2 = instructor_courses[j]
                
                # Get timeslots
                time1 = TimeSlot.query.get(course1.time_slot_id)
                time2 = TimeSlot.query.get(course2.time_slot_id)
                
                # Check if timeslots overlap
                if time1 and time2 and time1.day == time2.day:
                    # Convert times to comparable format (assuming times are stored as strings like "HH:MM")
                    start1 = time1.start_time
                    end1 = time1.end_time
                    start2 = time2.start_time
                    end2 = time2.end_time
                    
                    # Check for overlap
                    if (start1 <= start2 < end1) or (start1 < end2 <= end1) or (start2 <= start1 < end2):
                        instructor_conflicts.append({
                            'instructor': instructor,
                            'time_slot1': time1,
                            'time_slot2': time2,
                            'courses': [course1, course2]
                        })
    
    # Find classroom conflicts (multiple courses in same classroom at same time)
    classroom_conflicts = []
    from models import Classroom
    classrooms = Classroom.query.all()
    
    for classroom in classrooms:
        # Get classroom's scheduled courses
        classroom_courses = Course.query.filter(
            Course.classroom_id == classroom.id,
            Course.time_slot_id.isnot(None)
        ).all()
        
        # Group courses by time slot
        courses_by_timeslot = {}
        for course in classroom_courses:
            if course.time_slot_id not in courses_by_timeslot:
                courses_by_timeslot[course.time_slot_id] = []
            courses_by_timeslot[course.time_slot_id].append(course)
        
        # Find conflicts (more than one course in a time slot)
        for time_slot_id, courses in courses_by_timeslot.items():
            if len(courses) > 1:
                classroom_conflicts.append({
                    'classroom': classroom,
                    'time_slot': TimeSlot.query.get(time_slot_id),
                    'courses': courses
                })
    
    total_conflicts = len(student_conflicts) + len(instructor_conflicts) + len(classroom_conflicts)
    
    return render_template('conflicts.html', 
                          student_conflicts=student_conflicts,
                          instructor_conflicts=instructor_conflicts,
                          classroom_conflicts=classroom_conflicts,
                          total_conflicts=total_conflicts)

@conflicts_bp.route('/graph')
def view_graph():
    try:
        # First, try to downgrade numpy or handle the compatibility issue
        import os
        os.environ['MPLBACKEND'] = 'Agg'
        
        import networkx as nx
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import io
        import base64
        from collections import defaultdict
        
        # Clear any existing plots
        plt.clf()
        
    except ImportError as e:
        return render_template('graph.html', 
                             error_message=f"Required libraries are not properly installed. Error: {str(e)}")
    except Exception as e:
        return render_template('graph.html', 
                             error_message=f"Graph library initialization failed: {str(e)}")
    
    try:
        # Create graph
        G = nx.Graph()
        
        # Get all courses
        courses = Course.query.all()
        
        if not courses:
            return render_template('graph.html', 
                                 error_message="No courses found. Please add courses before generating the graph.",
                                 graph_image=None)
        
        # Add nodes (courses) with labels
        course_dict = {}
        for course in courses:
            G.add_node(course.id, label=f"{course.code}\n{course.name[:15]}...")
            course_dict[course.id] = course
        
        # Track conflicts for edge creation
        conflicts_found = 0
        
        # Add edges for student enrollment conflicts
        student_courses = defaultdict(list)
        for course in courses:
            if course.time_slot_id:  # Only consider courses with assigned timeslots
                for student in course.students:
                    student_courses[student.id].append(course)
        
        # Create edges between courses that share students AND have overlapping times
        for student_id, student_course_list in student_courses.items():
            for i in range(len(student_course_list)):
                for j in range(i + 1, len(student_course_list)):
                    course1 = student_course_list[i]
                    course2 = student_course_list[j]
                    
                    # Get timeslots
                    time1 = TimeSlot.query.get(course1.time_slot_id)
                    time2 = TimeSlot.query.get(course2.time_slot_id)
                    
                    # Only add edge if there's a time conflict
                    if time1 and time2 and time1.day == time2.day:
                        # Check for time overlap
                        start1 = time1.start_time
                        end1 = time1.end_time
                        start2 = time2.start_time
                        end2 = time2.end_time
                        
                        if (start1 <= start2 < end1) or (start1 < end2 <= end1) or (start2 <= start1 < end2):
                            if not G.has_edge(course1.id, course2.id):
                                G.add_edge(course1.id, course2.id, conflict_type='student')
                                conflicts_found += 1
        
        # Add edges for instructor conflicts
        instructor_courses = defaultdict(list)
        for course in courses:
            if course.instructor_id and course.time_slot_id:
                instructor_courses[course.instructor_id].append(course)
        
        # Create edges between courses that share instructors AND have overlapping times
        for instructor_id, instructor_course_list in instructor_courses.items():
            for i in range(len(instructor_course_list)):
                for j in range(i + 1, len(instructor_course_list)):
                    course1 = instructor_course_list[i]
                    course2 = instructor_course_list[j]
                    
                    # Get timeslots
                    time1 = TimeSlot.query.get(course1.time_slot_id)
                    time2 = TimeSlot.query.get(course2.time_slot_id)
                    
                    # Only add edge if there's a time conflict
                    if time1 and time2 and time1.day == time2.day:
                        # Check for time overlap
                        start1 = time1.start_time
                        end1 = time1.end_time
                        start2 = time2.start_time
                        end2 = time2.end_time
                        
                        if (start1 <= start2 < end1) or (start1 < end2 <= end1) or (start2 <= start1 < end2):
                            if not G.has_edge(course1.id, course2.id):
                                G.add_edge(course1.id, course2.id, conflict_type='instructor')
                                conflicts_found += 1
        
        # Add edges for classroom conflicts (same time and room)
        time_classroom_courses = defaultdict(list)
        for course in courses:
            if course.time_slot_id and course.classroom_id:
                key = (course.time_slot_id, course.classroom_id)
                time_classroom_courses[key].append(course.id)
        
        # Create edges for classroom conflicts
        for key, course_ids in time_classroom_courses.items():
            for i in range(len(course_ids)):
                for j in range(i + 1, len(course_ids)):
                    if not G.has_edge(course_ids[i], course_ids[j]):
                        G.add_edge(course_ids[i], course_ids[j], conflict_type='classroom')
                        conflicts_found += 1
          # Create the plot
        plt.figure(figsize=(12, 10))
        plt.clf()
        
        if G.number_of_nodes() == 0:
            plt.text(0.5, 0.5, 'No courses available for graph generation', 
                    horizontalalignment='center', verticalalignment='center', 
                    transform=plt.gca().transAxes, fontsize=16)
            plt.axis('off')
        else:
            # Use spring layout with fixed seed for consistent positioning
            import random
            random.seed(42)  # Fixed seed for consistent layout
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=1000, alpha=0.7)
            
            # Draw edges with different colors for different conflict types
            if G.number_of_edges() > 0:
                # Separate edges by conflict type
                student_edges = []
                instructor_edges = []
                classroom_edges = []
                
                for edge in G.edges(data=True):
                    conflict_type = edge[2].get('conflict_type', 'unknown')
                    edge_tuple = (edge[0], edge[1])
                    if conflict_type == 'student':
                        student_edges.append(edge_tuple)
                    elif conflict_type == 'instructor':
                        instructor_edges.append(edge_tuple)
                    elif conflict_type == 'classroom':
                        classroom_edges.append(edge_tuple)
                
                # Draw edges by type with different colors
                if student_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=student_edges, 
                                         edge_color='red', alpha=0.6, width=2)
                if instructor_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=instructor_edges, 
                                         edge_color='orange', alpha=0.6, width=2)
                if classroom_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=classroom_edges, 
                                         edge_color='purple', alpha=0.6, width=2)
            
            # Draw labels
            labels = {}
            for node in G.nodes():
                course = course_dict.get(node)
                if course:
                    labels[node] = course.code
                else:
                    labels[node] = str(node)
            
            nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
            
            # Add title and legend
            plt.title(f'Course Conflict Graph\n{G.number_of_nodes()} Courses, {G.number_of_edges()} Conflicts', 
                     fontsize=16, fontweight='bold', pad=20)
            
            # Create legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='red', lw=3, label='Student Conflicts'),
                Line2D([0], [0], color='orange', lw=3, label='Instructor Conflicts'),
                Line2D([0], [0], color='purple', lw=3, label='Classroom Conflicts')
            ]
            plt.legend(handles=legend_elements, loc='upper right')
            
            plt.axis('off')
        
        # Save the plot to a BytesIO object
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        
        # Convert to base64 string
        graph_image = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Close the plot to free memory
        plt.close()
        
        # Prepare statistics
        stats = {
            'total_courses': G.number_of_nodes(),
            'total_conflicts': G.number_of_edges(),
            'conflicts_found': conflicts_found
        }
        
        return render_template('graph.html', 
                             graph_image=graph_image,
                             stats=stats,
                             error_message=None)
        
    except Exception as e:
        # Make sure to close any open plots
        try:
            plt.close()
        except:
            pass
        
        return render_template('graph.html', 
                             error_message=f"Failed to generate graph: {str(e)}",
                             graph_image=None)
    # for student in Student.query.all():
    #     student_courses = student.courses
    #     for i, course1 in enumerate(student_courses):
    #         for course2 in student_courses[i+1:]:
    #             if G.has_edge(course1.id, course2.id):
    #                 # Edge already exists, increment weight
    #                 G[course1.id][course2.id]['weight'] += 1
    #             else:
    #                 # Add new edge with weight 1
    #                 G.add_edge(course1.id, course2.id, weight=1, type='student')
    
    # # Add edges for instructor conflicts
    # for instructor in Instructor.query.all():
    #     instructor_courses = Course.query.filter_by(instructor_id=instructor.id).all()
    #     for i, course1 in enumerate(instructor_courses):
    #         for course2 in instructor_courses[i+1:]:
    #             # Add edge with high weight for instructor conflicts
    #             if G.has_edge(course1.id, course2.id):
    #                 G[course1.id][course2.id]['weight'] = 10
    #                 G[course1.id][course2.id]['type'] = 'instructor'
    #             else:
    #                 G.add_edge(course1.id, course2.id, weight=10, type='instructor')
    
    # if not courses:
    #     return render_template('graph.html', 
    #                          error_message="No courses available to generate graph.")
    
    # # Generate graph image
    # plt.figure(figsize=(12, 8))
    # pos = nx.spring_layout(G) if G.nodes() else {}
    
    # # Draw regular edges (student conflicts)
    # student_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'student']
    # if student_edges:
    #     nx.draw_networkx_edges(G, pos, edgelist=student_edges, width=1, alpha=0.5, edge_color='gray')
    
    # # Draw instructor conflict edges
    # instructor_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'instructor']
    # if instructor_edges:
    #     nx.draw_networkx_edges(G, pos, edgelist=instructor_edges, width=2, alpha=0.7, edge_color='red')
    
    # # Draw nodes
    # if G.nodes():
    #     nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
        
    #     # Draw labels
    #     course_labels = {course.id: course.code for course in courses}
    #     nx.draw_networkx_labels(G, pos, labels=course_labels, font_size=10)
    
    # plt.title("Course Conflict Graph")
    # plt.axis('off')
    
    # # Save to buffer
    # img_buf = io.BytesIO()
    # plt.savefig(img_buf, format='png', bbox_inches='tight', dpi=100)
    # img_buf.seek(0)
    # img_data = base64.b64encode(img_buf.read()).decode('utf-8')
    # plt.close()
    
    # return render_template('graph.html', graph_image=img_data)
