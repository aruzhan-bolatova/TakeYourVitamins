#!/bin/bash

# Check if server is running
function check_server {
    curl -s http://localhost:5001/api/auth/login > /dev/null
    if [ $? -ne 0 ]; then
        echo "Error: Server is not running. Please start the server first with: python run.py"
        exit 1
    fi
}

# Create directories if they don't exist
mkdir -p jmeter/results

# Display menu
function show_menu {
    clear
    echo "===== TakeYourVitamins JMeter Performance Tests ====="
    echo "1. Run Load Test (Baseline)"
    echo "2. Run Spike Test"
    echo "3. Run Custom Test"
    echo "4. Generate HTML Report"
    echo "5. Exit"
    echo "=================================================="
    echo "Enter your choice [1-5]: "
}

# Run load test with default or custom parameters
function run_load_test {
    echo "Running load test..."
    threads=${1:-5}
    rampup=${2:-10}
    loops=${3:-20}
    
    jmeter -n -t jmeter/plans/TYVLoadTest.jmx \
        -Jthreads=$threads \
        -Jrampup=$rampup \
        -Jloops=$loops \
        -l jmeter/results/load_test_results.jtl
    
    echo "Load test completed. Results saved to jmeter/results/load_test_results.jtl"
}

# Run spike test with default or custom parameters
function run_spike_test {
    echo "Running spike test..."
    spike_threads=${1:-50}
    spike_duration=${2:-60}
    startup_time=${3:-10}
    recovery_time=${4:-20}
    
    jmeter -n -t jmeter/plans/TYVSpikeTest.jmx \
        -Jspike_threads=$spike_threads \
        -Jspike_duration=$spike_duration \
        -Jstartup_time=$startup_time \
        -Jrecovery_time=$recovery_time \
        -l jmeter/results/spike_test_results.jtl
    
    echo "Spike test completed. Results saved to jmeter/results/spike_test_results.jtl"
}

# Generate HTML report from test results
function generate_report {
    results_file=$1
    report_dir=$2
    
    if [ ! -f "$results_file" ]; then
        echo "Error: Results file $results_file not found!"
        return 1
    fi
    
    jmeter -g $results_file -e -o $report_dir
    echo "Report generated successfully at $report_dir"
}

# Main application loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)  # Load Test
            check_server
            echo "Running load test with default parameters..."
            echo "Threads: 5, Ramp-up: 10 seconds, Loops: 20"
            run_load_test 5 10 20
            echo "Press Enter to continue..."
            read
            ;;
        2)  # Spike Test
            check_server
            echo "Running spike test with default parameters..."
            echo "Spike Threads: 50, Duration: 60 seconds, Startup Time: 10 seconds, Recovery Time: 20 seconds"
            run_spike_test 50 60 10 20
            echo "Press Enter to continue..."
            read
            ;;
        3)  # Custom Test
            check_server
            echo "Select test type:"
            echo "1. Load Test"
            echo "2. Spike Test"
            read test_type
            
            if [ "$test_type" == "1" ]; then
                echo "Enter number of threads (default: 5):"
                read threads
                threads=${threads:-5}
                
                echo "Enter ramp-up period in seconds (default: 10):"
                read rampup
                rampup=${rampup:-10}
                
                echo "Enter number of loops (default: 20):"
                read loops
                loops=${loops:-20}
                
                run_load_test $threads $rampup $loops
            elif [ "$test_type" == "2" ]; then
                echo "Enter number of spike threads (default: 50):"
                read spike_threads
                spike_threads=${spike_threads:-50}
                
                echo "Enter test duration in seconds (default: 60):"
                read spike_duration
                spike_duration=${spike_duration:-60}
                
                echo "Enter startup time in seconds (default: 10):"
                read startup_time
                startup_time=${startup_time:-10}
                
                echo "Enter recovery time in seconds (default: 20):"
                read recovery_time
                recovery_time=${recovery_time:-20}
                
                run_spike_test $spike_threads $spike_duration $startup_time $recovery_time
            else
                echo "Invalid test type!"
            fi
            echo "Press Enter to continue..."
            read
            ;;
        4)  # Generate Report
            echo "Select report to generate:"
            echo "1. Load Test Report"
            echo "2. Spike Test Report"
            read report_type
            
            timestamp=$(date +"%Y%m%d-%H%M%S")
            
            if [ "$report_type" == "1" ]; then
                if [ -f "jmeter/results/load_test_results.jtl" ]; then
                    generate_report "jmeter/results/load_test_results.jtl" "jmeter/results/load-report-$timestamp"
                else
                    echo "No load test results found. Run a load test first."
                fi
            elif [ "$report_type" == "2" ]; then
                if [ -f "jmeter/results/spike_test_results.jtl" ]; then
                    generate_report "jmeter/results/spike_test_results.jtl" "jmeter/results/spike-report-$timestamp"
                else
                    echo "No spike test results found. Run a spike test first."
                fi
            else
                echo "Invalid report type!"
            fi
            echo "Press Enter to continue..."
            read
            ;;
        5)  # Exit
            echo "Exiting..."
            exit 0
            ;;
        *)  # Invalid option
            echo "Invalid option. Press Enter to continue..."
            read
            ;;
    esac
done 