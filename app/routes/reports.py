from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.intake_log import IntakeLog
from app.models.symptom_log import SymptomLog
from app.models.supplement import Supplement
from app.middleware.auth import check_user_access
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# Create the blueprint
bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@bp.route('/<user_id>', methods=['GET'])
@jwt_required()
@check_user_access
def get_user_report(user_id):
    """Get a report for a specific user"""
    # Standard response structure with defaults
    report_data = {
        "userId": user_id,
        "reportType": "weekly",  # Default
        "startDate": "",
        "endDate": "",
        "intakeSummary": [],
        "symptomSummary": [],
        "correlations": [],
        "streaks": [],
        "progress": {
            "supplementProgress": [],
            "overallTrends": {
                "totalSupplements": 0,
                "monthlyTotals": [],
                "consistencyTrend": "stable"
            },
            "milestones": []
        },
        "recommendations": []
    }
    
    try:
        # Get report type from query parameters
        report_type = request.args.get('range', 'weekly').lower()
        
        # Validate report type
        valid_types = ['daily', 'weekly', 'monthly', 'yearly']
        if report_type not in valid_types:
            return jsonify({"error": f"Invalid report type. Must be one of: {', '.join(valid_types)}"}), 400
        
        # Set report type in response
        report_data["reportType"] = report_type
        
        # Get date range for report
        end_date = datetime.now()
        
        if report_type == 'daily':
            start_date = end_date - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=30)
        elif report_type == 'yearly':
            start_date = end_date - timedelta(days=365)
        
        # Format dates for MongoDB query
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        # Set date range in response
        report_data["startDate"] = start_str
        report_data["endDate"] = end_str

        # Safely retrieve data with individual error handling for each section
        # This ensures that one section failing won't crash the entire report
        
        # 1. Get intake logs with error handling
        try:
            intake_logs = IntakeLog.find_by_date_range(user_id, start_str, end_str)
        except Exception as e:
            import logging
            logging.error(f"Error fetching intake logs: {e}")
            intake_logs = []
        
        # 2. Get symptom logs with error handling
        try:
            symptom_logs = SymptomLog.find_by_date_range(user_id, start_str, end_str)
        except Exception as e:
            import logging
            logging.error(f"Error fetching symptom logs: {e}")
            symptom_logs = []
        
        # 3. Generate each section of the report with individual error handling
        
        # Intake summary
        try:
            report_data["intakeSummary"] = _generate_intake_summary(intake_logs)
        except Exception as e:
            import logging
            logging.error(f"Error generating intake summary: {e}")
        
        # Symptom summary
        try:
            report_data["symptomSummary"] = _generate_symptom_summary(symptom_logs)
        except Exception as e:
            import logging
            logging.error(f"Error generating symptom summary: {e}")
        
        # Correlations
        try:
            report_data["correlations"] = _analyze_correlations(intake_logs, symptom_logs)
        except Exception as e:
            import logging
            logging.error(f"Error analyzing correlations: {e}")
        
        # Streaks
        try:
            # _calculate_streaks now returns a flat list of supplement streaks directly
            report_data["streaks"] = _calculate_streaks(user_id, intake_logs)
        except Exception as e:
            import logging
            logging.error(f"Error calculating streaks: {e}")
        
        # Progress
        try:
            report_data["progress"] = _calculate_progress(user_id, intake_logs)
        except Exception as e:
            import logging
            logging.error(f"Error calculating progress: {e}")
        
        # Recommendations
        try:
            report_data["recommendations"] = _generate_recommendations(user_id, intake_logs, symptom_logs)
        except Exception as e:
            import logging
            logging.error(f"Error generating recommendations: {e}")
        
        # Return report
        return jsonify(report_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import logging
        logging.error(f"Error generating full report: {e}")
        # Return partial report with error indicator
        report_data["error"] = "Partial data available due to processing issues"
        return jsonify(report_data), 200  # Return 200 with partial data instead of 500

@bp.route('/streaks/<user_id>', methods=['GET'])
@jwt_required()
@check_user_access
def get_user_streaks(user_id):
    """Get streak information for a specific user"""
    # Default response structure
    response_data = {
        "userId": user_id,
        "streaks": []
    }
    
    try:
        # Get intake logs for the user (limit to last 365 days for performance)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Format dates for MongoDB query
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        # Get intake logs with error handling
        try:
            intake_logs = IntakeLog.find_by_date_range(user_id, start_str, end_str)
        except Exception as e:
            import logging
            logging.error(f"Error fetching intake logs for streaks: {e}")
            intake_logs = []
        
        # Calculate streaks with error handling
        try:
            # _calculate_streaks now returns a flat list of supplement streaks
            response_data["streaks"] = _calculate_streaks(user_id, intake_logs)
        except Exception as e:
            import logging
            logging.error(f"Error calculating streaks: {e}")
        
        # Return streaks
        return jsonify(response_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import logging
        logging.error(f"Error generating streaks: {e}")
        # Return partial data with error indicator
        response_data["error"] = "Partial data available due to processing issues"
        return jsonify(response_data), 200  # Return 200 with partial data instead of 500

@bp.route('/progress/<user_id>', methods=['GET'])
@jwt_required()
@check_user_access
def get_user_progress(user_id):
    """Get progress information for a specific user"""
    # Default response structure
    response_data = {
        "userId": user_id,
        "progress": {
            "supplementProgress": [],
            "overallTrends": {
                "totalSupplements": 0,
                "monthlyTotals": [],
                "consistencyTrend": "stable"
            },
            "milestones": []
        }
    }
    
    try:
        # Get intake logs for the user (limit to last 365 days for performance)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Format dates for MongoDB query
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        # Get intake logs with error handling
        try:
            intake_logs = IntakeLog.find_by_date_range(user_id, start_str, end_str)
        except Exception as e:
            import logging
            logging.error(f"Error fetching intake logs for progress: {e}")
            intake_logs = []
        
        # Calculate progress with error handling
        try:
            response_data["progress"] = _calculate_progress(user_id, intake_logs)
        except Exception as e:
            import logging
            logging.error(f"Error calculating progress: {e}")
        
        # Return progress
        return jsonify(response_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import logging
        logging.error(f"Error generating progress data: {e}")
        # Return partial data with error indicator
        response_data["error"] = "Partial data available due to processing issues"
        return jsonify(response_data), 200  # Return 200 with partial data instead of 500

# Helper functions for report generation

def _generate_intake_summary(intake_logs):
    """Generate a summary of intake logs"""
    # Group intake logs by supplement
    supplements = {}
    for log in intake_logs:
        supp_id = log.supplement_id
        if supp_id not in supplements:
            supplements[supp_id] = {
                'supplementId': supp_id,
                'name': log.supplement_name if hasattr(log, 'supplement_name') else 'Unknown',
                'count': 0,
                'dates': [],
                'dosages': [],
                'timings': [],
                'notes': []
            }
        
        supplements[supp_id]['count'] += 1
        supplements[supp_id]['dates'].append(log.timestamp)
        
        if hasattr(log, 'dosage') and log.dosage:
            supplements[supp_id]['dosages'].append(log.dosage)
            
        if hasattr(log, 'timing') and log.timing:
            supplements[supp_id]['timings'].append(log.timing)
            
        if hasattr(log, 'notes') and log.notes:
            supplements[supp_id]['notes'].append(log.notes)
    
    # Calculate total days and consistency for each supplement
    for supp_id in supplements:
        # Get unique dates
        unique_dates = set()
        for date_str in supplements[supp_id]['dates']:
            try:
                date = datetime.fromisoformat(date_str)
                unique_dates.add(date.date())
            except (ValueError, TypeError):
                pass
                
        supplements[supp_id]['uniqueDays'] = len(unique_dates)
        
        # Calculate most common dosage
        dosages = supplements[supp_id]['dosages']
        if dosages:
            # Count occurrences of each dosage
            dosage_counts = {}
            for dosage in dosages:
                dosage_counts[dosage] = dosage_counts.get(dosage, 0) + 1
                
            # Find most common
            most_common_dosage = max(dosage_counts.items(), key=lambda x: x[1])[0]
            supplements[supp_id]['mostCommonDosage'] = most_common_dosage
            
        # Calculate most common timing
        timings = supplements[supp_id]['timings']
        if timings:
            # Count occurrences of each timing
            timing_counts = {}
            for timing in timings:
                timing_counts[timing] = timing_counts.get(timing, 0) + 1
                
            # Find most common
            most_common_timing = max(timing_counts.items(), key=lambda x: x[1])[0]
            supplements[supp_id]['mostCommonTiming'] = most_common_timing
    
    return list(supplements.values())

def _generate_symptom_summary(symptom_logs):
    """Generate a summary of symptom logs"""
    try:
        # Group symptom logs by symptom (not symptom_type which doesn't exist)
        symptoms = {}
        for log in symptom_logs:
            # Use the 'symptom' property instead of 'symptom_type'
            symptom = getattr(log, 'symptom', None)
            if not symptom:
                continue  # Skip logs without a valid symptom
                
            if symptom not in symptoms:
                symptoms[symptom] = {
                    'symptom': symptom,
                    'count': 0,
                    'dates': [],
                    'severities': [],
                    'notes': []
                }
            
            symptoms[symptom]['count'] += 1
            
            # Safely access timestamp with a fallback
            timestamp = getattr(log, 'timestamp', None) or getattr(log, 'logDate', None)
            if timestamp:
                symptoms[symptom]['dates'].append(timestamp)
            
            # Safely access severity
            severity = getattr(log, 'severity', None) or getattr(log, 'rating', None)
            if severity is not None:  # Allow 0 severity
                symptoms[symptom]['severities'].append(severity)
                
            # Safely access notes
            notes = getattr(log, 'notes', None) or getattr(log, 'comments', None)
            if notes:
                symptoms[symptom]['notes'].append(notes)
        
        # Calculate averages and trends for each symptom
        for symptom in symptoms:
            # Calculate average severity
            severities = symptoms[symptom]['severities']
            if severities and all(s is not None and isinstance(s, (int, float)) for s in severities):
                avg_severity = sum(severities) / len(severities)
                symptoms[symptom]['averageSeverity'] = round(avg_severity, 1)
            else:
                symptoms[symptom]['averageSeverity'] = 0  # Default value
                
            # Sort dates for trend analysis
            dates = []
            for date_str in symptoms[symptom]['dates']:
                try:
                    date = datetime.fromisoformat(date_str)
                    dates.append(date)
                except (ValueError, TypeError):
                    pass
                    
            # Sort dates
            dates.sort()
            
            # If we have severities that match dates, calculate trend
            if len(dates) >= 3 and len(dates) == len(severities):
                # Check if severity is increasing, decreasing, or stable
                first_half = severities[:len(severities)//2]
                second_half = severities[len(severities)//2:]
                
                avg_first = sum(first_half) / len(first_half)
                avg_second = sum(second_half) / len(second_half)
                
                if avg_second > avg_first * 1.1:  # 10% increase
                    symptoms[symptom]['trend'] = 'increasing'
                elif avg_second < avg_first * 0.9:  # 10% decrease
                    symptoms[symptom]['trend'] = 'decreasing'
                else:
                    symptoms[symptom]['trend'] = 'stable'
        
        return list(symptoms.values())
    except Exception as e:
        # Log the error and return an empty list instead of crashing
        import logging
        logging.error(f"Error in _generate_symptom_summary: {e}")
        return []

def _analyze_correlations(intake_logs, symptom_logs):
    """Analyze correlations between intake and symptoms"""
    try:
        # This is a simplified analysis
        # In a real implementation, this would use more sophisticated statistical methods
        
        correlations = []
        
        # Skip analysis if we have insufficient data
        if not intake_logs or not symptom_logs:
            return []
        
        # Group intake logs by supplement and day
        supplement_days = {}
        for log in intake_logs:
            supp_id = getattr(log, 'supplement_id', None)
            if not supp_id:
                continue
                
            try:
                timestamp = getattr(log, 'timestamp', None)
                if not timestamp:
                    continue
                
                date = datetime.fromisoformat(timestamp).date()
                if supp_id not in supplement_days:
                    supplement_days[supp_id] = set()
                supplement_days[supp_id].add(date)
            except (ValueError, TypeError, AttributeError):
                continue
        
        # Group symptom logs by symptom name (not type) and day
        symptom_days = {}
        for log in symptom_logs:
            # Use the correct 'symptom' property instead of 'symptom_type'
            symptom = getattr(log, 'symptom', None)
            if not symptom:
                continue
                
            try:
                # Try different property names for timestamp
                timestamp = getattr(log, 'timestamp', None) or getattr(log, 'logDate', None)
                if not timestamp:
                    continue
                
                date = datetime.fromisoformat(timestamp).date()
                
                # Try different property names for severity
                severity = getattr(log, 'severity', None) or getattr(log, 'rating', None)
                
                if symptom not in symptom_days:
                    symptom_days[symptom] = []
                symptom_days[symptom].append((date, severity))
            except (ValueError, TypeError, AttributeError):
                continue
        
        # Check for correlations
        for supp_id, supp_dates in supplement_days.items():
            for symptom, symptom_data in symptom_days.items():
                # Check for symptom occurrences within 2 days of supplement intake
                potential_correlations = []
                
                for date in supp_dates:
                    # Check for symptoms on the same day or within 2 days after
                    for symptom_date, severity in symptom_data:
                        if date <= symptom_date <= date + timedelta(days=2):
                            potential_correlations.append({
                                'intakeDate': date.isoformat(),
                                'symptomDate': symptom_date.isoformat(),
                                'daysDifference': (symptom_date - date).days,
                                'severity': severity
                            })
                
                # If we have enough potential correlations, consider it significant
                if len(potential_correlations) >= 3:
                    # Get supplement info - but handle potential errors
                    supplement_name = 'Unknown Supplement'
                    try:
                        # Use find_by_id only if the ID looks valid
                        if supp_id and isinstance(supp_id, (str, ObjectId)):
                            supplement = Supplement.find_by_id(supp_id)
                            if supplement and hasattr(supplement, 'name'):
                                supplement_name = supplement.name
                    except Exception:
                        pass
                    
                    # Calculate correlation strength (0-1)
                    correlation_strength = min(1.0, len(potential_correlations) / 10)
                    
                    # Calculate confidence level (0-1)
                    # Higher confidence for more occurrences and shorter time gaps
                    avg_days_diff = sum(c['daysDifference'] for c in potential_correlations) / len(potential_correlations)
                    confidence = correlation_strength * (1 - min(1, avg_days_diff/2))
                    
                    correlation = {
                        'supplementId': supp_id,
                        'supplementName': supplement_name,
                        'symptom': symptom,
                        'correlationStrength': round(correlation_strength, 2),
                        'confidence': round(confidence, 2),
                        'description': f"Potential relationship between {supplement_name} and {symptom}",
                        'occurrences': len(potential_correlations)
                    }
                    
                    correlations.append(correlation)
        
        return correlations
    except Exception as e:
        # Log error and return empty list rather than crashing
        import logging
        logging.error(f"Error in _analyze_correlations: {e}")
        return []

def _calculate_streaks(user_id, intake_logs):
    """Calculate streaks for a user"""
    # Group logs by date
    date_logs = {}
    for log in intake_logs:
        try:
            date = datetime.fromisoformat(log.timestamp).date()
            if date not in date_logs:
                date_logs[date] = []
            date_logs[date].append(log)
        except (ValueError, TypeError, AttributeError):
            pass
    
    # Sort dates
    sorted_dates = sorted(date_logs.keys())
    
    # Calculate current streak
    current_streak = 0
    today = datetime.now().date()
    
    # Check if there is a log for today
    if today in date_logs:
        current_streak = 1
        
        # Check previous days
        check_date = today - timedelta(days=1)
        while check_date in date_logs:
            current_streak += 1
            check_date -= timedelta(days=1)
    
    # Calculate longest streak
    longest_streak = 0
    current_run = 0
    
    for i in range(len(sorted_dates)):
        if i == 0:
            current_run = 1
        else:
            # Check if this date is consecutive with the previous one
            prev_date = sorted_dates[i-1]
            curr_date = sorted_dates[i]
            
            if (curr_date - prev_date).days == 1:
                current_run += 1
            else:
                # Streak broken, reset
                longest_streak = max(longest_streak, current_run)
                current_run = 1
    
    # Check if the final run is the longest
    longest_streak = max(longest_streak, current_run)
    
    # Calculate supplement streaks
    supplement_streaks = []
    
    for log in intake_logs:
        supp_id = log.supplement_id
        if not supp_id:
            continue
            
        try:
            date = datetime.fromisoformat(log.timestamp).date()
            
            # Check if this supplement is already in our list
            existing_supp = next((s for s in supplement_streaks if s['supplementId'] == supp_id), None)
            
            if not existing_supp:
                supplement_name = log.supplement_name if hasattr(log, 'supplement_name') else 'Unknown'
                existing_supp = {
                    'supplementId': supp_id,
                    'supplementName': supplement_name,
                    'dates': set(),
                    'currentStreak': 0,
                    'longestStreak': 0,
                    'lastTaken': log.timestamp  # Add lastTaken field for frontend
                }
                supplement_streaks.append(existing_supp)
                
            existing_supp['dates'].add(date)
            
            # Update lastTaken if this log is more recent
            try:
                log_date = datetime.fromisoformat(log.timestamp)
                last_taken = datetime.fromisoformat(existing_supp['lastTaken'])
                if log_date > last_taken:
                    existing_supp['lastTaken'] = log.timestamp
            except (ValueError, TypeError):
                pass
                
        except (ValueError, TypeError, AttributeError):
            pass
    
    # Calculate streaks for each supplement
    for data in supplement_streaks:
        # Sort dates
        sorted_supp_dates = sorted(data['dates'])
        
        # Calculate current streak
        current_supp_streak = 0
        
        # Check if there is a log for today
        if today in data['dates']:
            current_supp_streak = 1
            
            # Check previous days
            check_date = today - timedelta(days=1)
            while check_date in data['dates']:
                current_supp_streak += 1
                check_date -= timedelta(days=1)
        
        # Calculate longest streak
        longest_supp_streak = 0
        current_supp_run = 0
        
        for i in range(len(sorted_supp_dates)):
            if i == 0:
                current_supp_run = 1
            else:
                # Check if this date is consecutive with the previous one
                prev_date = sorted_supp_dates[i-1]
                curr_date = sorted_supp_dates[i]
                
                if (curr_date - prev_date).days == 1:
                    current_supp_run += 1
                else:
                    # Streak broken, reset
                    longest_supp_streak = max(longest_supp_streak, current_supp_run)
                    current_supp_run = 1
        
        # Check if the final run is the longest
        longest_supp_streak = max(longest_supp_streak, current_supp_run)
        
        # Update streak data
        data['currentStreak'] = current_supp_streak
        data['longestStreak'] = longest_supp_streak
        
        # Remove the dates set since we don't need it in the response
        # and it can't be JSON serialized
        data.pop('dates', None)
    
    # For now, return only supplement streaks as a flat list
    # This matches the frontend's expectations
    return supplement_streaks

def _calculate_progress(user_id, intake_logs):
    """Calculate progress for a user"""
    # Group logs by supplement and month
    monthly_logs = {}
    
    for log in intake_logs:
        supp_id = log.supplement_id
        if not supp_id:
            continue
            
        try:
            date = datetime.fromisoformat(log.timestamp)
            month_key = f"{date.year}-{date.month:02d}"
            
            if month_key not in monthly_logs:
                monthly_logs[month_key] = {}
                
            if supp_id not in monthly_logs[month_key]:
                monthly_logs[month_key][supp_id] = {
                    'supplementId': supp_id,
                    'supplementName': log.supplement_name if hasattr(log, 'supplement_name') else 'Unknown',
                    'count': 0,
                    'dates': set()
                }
                
            monthly_logs[month_key][supp_id]['count'] += 1
            monthly_logs[month_key][supp_id]['dates'].add(date.date())
        except (ValueError, TypeError, AttributeError):
            pass
    
    # Calculate progress metrics
    months = sorted(monthly_logs.keys())
    
    # Calculate consistency for each supplement over time
    supplement_progress = {}
    
    for month in months:
        for supp_id, data in monthly_logs[month].items():
            if supp_id not in supplement_progress:
                supplement_progress[supp_id] = {
                    'supplementId': supp_id,
                    'supplementName': data['supplementName'],
                    'monthlyData': []
                }
                
            # Calculate consistency (days taken / days in month)
            year, month_num = map(int, month.split('-'))
            days_in_month = 30  # Approximation
            consistency = round(len(data['dates']) / days_in_month * 100, 1)
            
            supplement_progress[supp_id]['monthlyData'].append({
                'month': month,
                'count': data['count'],
                'uniqueDays': len(data['dates']),
                'consistency': consistency
            })
    
    # Calculate overall trends
    overall_trends = {
        'totalSupplements': len(supplement_progress),
        'monthlyTotals': [],
        'consistencyTrend': 'increasing'  # Default value
    }
    
    # Calculate monthly totals
    for month in months:
        month_data = monthly_logs[month]
        total_count = sum(data['count'] for data in month_data.values())
        total_days = sum(len(data['dates']) for data in month_data.values())
        
        overall_trends['monthlyTotals'].append({
            'month': month,
            'totalCount': total_count,
            'totalUniqueDays': total_days
        })
    
    # Calculate consistency trend if we have at least 2 months of data
    if len(months) >= 2:
        # Compare first and last month
        first_month = months[0]
        last_month = months[-1]
        
        # Get average consistency for first and last month
        first_month_consistencies = []
        for supp_id, data in monthly_logs[first_month].items():
            year, month_num = map(int, first_month.split('-'))
            days_in_month = 30  # Approximation
            consistency = len(data['dates']) / days_in_month * 100
            first_month_consistencies.append(consistency)
        
        last_month_consistencies = []
        for supp_id, data in monthly_logs[last_month].items():
            year, month_num = map(int, last_month.split('-'))
            days_in_month = 30  # Approximation
            consistency = len(data['dates']) / days_in_month * 100
            last_month_consistencies.append(consistency)
        
        # Calculate averages
        avg_first = sum(first_month_consistencies) / len(first_month_consistencies) if first_month_consistencies else 0
        avg_last = sum(last_month_consistencies) / len(last_month_consistencies) if last_month_consistencies else 0
        
        # Determine trend
        if avg_last > avg_first * 1.1:  # 10% increase
            overall_trends['consistencyTrend'] = 'increasing'
        elif avg_last < avg_first * 0.9:  # 10% decrease
            overall_trends['consistencyTrend'] = 'decreasing'
        else:
            overall_trends['consistencyTrend'] = 'stable'
    
    # Calculate milestones
    milestones = []
    
    # Total intake milestone
    total_intake = 0
    for month_data in monthly_logs.values():
        for supplement_data in month_data.values():
            # Supplement data is a dictionary with 'count' key
            total_intake += supplement_data['count']
    
    if total_intake >= 100:
        milestones.append({
            'type': 'totalIntake',
            'value': total_intake,
            'description': f"Taken supplements {total_intake} times"
        })
    
    # Consistency milestone
    max_consistency = 0
    for supp_data in supplement_progress.values():
        for month_data in supp_data['monthlyData']:
            max_consistency = max(max_consistency, month_data['consistency'])
    
    if max_consistency >= 90:
        milestones.append({
            'type': 'consistency',
            'value': max_consistency,
            'description': f"Achieved {max_consistency}% consistency with a supplement"
        })
    
    # Streak milestone
    max_streak = 0
    for supp_data in supplement_progress.values():
        for month_data in supp_data['monthlyData']:
            max_streak = max(max_streak, month_data['uniqueDays'])
    
    if max_streak >= 28:
        milestones.append({
            'type': 'streak',
            'value': max_streak,
            'description': f"Maintained a {max_streak}-day streak with a supplement"
        })
    
    return {
        'supplementProgress': list(supplement_progress.values()),
        'overallTrends': overall_trends,
        'milestones': milestones
    }

def _generate_recommendations(user_id, intake_logs, symptom_logs):
    """Generate recommendations based on intake and symptom data"""
    recommendations = []
    
    # Group intake logs by supplement
    supplement_data = {}
    for log in intake_logs:
        supp_id = log.supplement_id
        if not supp_id:
            continue
            
        if supp_id not in supplement_data:
            supplement_data[supp_id] = {
                'supplementId': supp_id,
                'supplementName': log.supplement_name if hasattr(log, 'supplement_name') else 'Unknown',
                'count': 0,
                'dates': set(),
                'dosages': [],
                'timings': []
            }
            
        supplement_data[supp_id]['count'] += 1
        
        try:
            date = datetime.fromisoformat(log.timestamp).date()
            supplement_data[supp_id]['dates'].add(date)
        except (ValueError, TypeError, AttributeError):
            pass
            
        if hasattr(log, 'dosage') and log.dosage:
            supplement_data[supp_id]['dosages'].append(log.dosage)
            
        if hasattr(log, 'timing') and log.timing:
            supplement_data[supp_id]['timings'].append(log.timing)
    
    # Check for consistency issues
    for supp_id, data in supplement_data.items():
        if len(data['dates']) >= 7:  # Only consider supplements taken for at least a week
            # Check consistency
            dates = sorted(data['dates'])
            days_span = (dates[-1] - dates[0]).days + 1
            consistency = len(dates) / days_span * 100
            
            if consistency < 70:  # Less than 70% consistent
                recommendations.append({
                    'type': 'consistency',
                    'supplementId': supp_id,
                    'supplementName': data['supplementName'],
                    'consistency': round(consistency, 1),
                    'message': f"Try to be more consistent with taking {data['supplementName']}. You've taken it on {len(dates)} out of {days_span} days.",
                    'priority': 'high' if consistency < 50 else 'medium'
                })
    
    # Check for timing consistency
    for supp_id, data in supplement_data.items():
        if len(data['timings']) >= 5:  # Only consider supplements with multiple timing records
            # Count occurrences of each timing
            timing_counts = {}
            for timing in data['timings']:
                timing_counts[timing] = timing_counts.get(timing, 0) + 1
                
            # Find most common timing
            most_common_timing = max(timing_counts.items(), key=lambda x: x[1])
            timing_consistency = most_common_timing[1] / len(data['timings']) * 100
            
            if timing_consistency < 70:  # Less than 70% consistent timing
                recommendations.append({
                    'type': 'timing',
                    'supplementId': supp_id,
                    'supplementName': data['supplementName'],
                    'message': f"Try to take {data['supplementName']} at a consistent time each day for better efficacy.",
                    'priority': 'medium'
                })
    
    # Check for symptoms that may be related to supplements
    symptom_counts = {}
    for log in symptom_logs:
        symptom_type = log.symptom_type
        if not symptom_type:
            continue
            
        if symptom_type not in symptom_counts:
            symptom_counts[symptom_type] = 0
            
        symptom_counts[symptom_type] += 1
    
    # If there are frequent symptoms, suggest tracking correlations
    frequent_symptoms = [symptom for symptom, count in symptom_counts.items() if count >= 3]
    if frequent_symptoms:
        recommendations.append({
            'type': 'tracking',
            'symptoms': frequent_symptoms,
            'message': f"Consider tracking your symptoms more closely to see if they correlate with specific supplements.",
            'priority': 'medium'
        })
    
    return recommendations 