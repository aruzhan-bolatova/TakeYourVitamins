# JMeter Performance Tests for TakeYourVitamins

This directory contains JMeter test plans and scripts to run performance tests against the TakeYourVitamins API.

## Prerequisites

- Apache JMeter (version 5.0 or higher)
- Running TakeYourVitamins server (on localhost:5001)

## Test Plans

The following test plans are available:

1. **TYVLoadTest.jmx** - Basic load test that simulates multiple users accessing the API
2. **TYVSpikeTest.jmx** - Spike test that simulates a sudden surge in traffic to the API

## Running Tests with Command Line

You can run the tests directly using JMeter's command-line interface:

### Load Test

```bash
jmeter -n -t jmeter/plans/TYVLoadTest.jmx -Jthreads=10 -Jrampup=30 -Jloops=50 -l jmeter/results/load_test_results.jtl
```

Parameters:
- `threads`: Number of concurrent users (default: 5)
- `rampup`: Time in seconds to ramp up to full number of threads (default: 10)
- `loops`: Number of times to repeat the test (default: 20)

### Spike Test

```bash
jmeter -n -t jmeter/plans/TYVSpikeTest.jmx -Jspike_threads=100 -Jspike_duration=120 -Jstartup_time=10 -Jrecovery_time=20 -l jmeter/results/spike_test_results.jtl
```

Parameters:
- `spike_threads`: Number of concurrent users during spike (default: 50)
- `spike_duration`: Duration of the whole test in seconds (default: 60)
- `startup_time`: Time in seconds before the spike begins (default: 5)
- `recovery_time`: Time in seconds for recovery after spike (default: 10)

### Generating Reports

To generate an HTML report from test results:

```bash
jmeter -g jmeter/results/test_results.jtl -e -o jmeter/results/report-directory
```

## Using the Automated Script

For convenience, a shell script is provided to help run common test scenarios:

```bash
./jmeter/run_tests.sh
```

This script provides a menu-driven interface to:
1. Run Load Test with default parameters
2. Run Spike Test with default parameters
3. Run Custom Test with user-defined parameters
4. Generate HTML Reports
5. Exit

## Interpreting Results

After running tests, you should look for:

- **Response time**: How long the server takes to respond to requests
- **Throughput**: Number of requests the server can handle per second
- **Error rate**: Percentage of requests that fail
- **Resource utilization**: CPU, memory, and network usage during tests

Good performance metrics for a web API typically include:
- Response times under 200ms for simple requests
- Throughput appropriate for expected user load
- Error rate below 1% under normal conditions
- Linear scaling of resource utilization with increased load

## Common Issues

- **Connection refused**: Make sure the TakeYourVitamins server is running on port 5001
- **Authentication errors**: The test plans include authentication steps for API endpoints
- **High error rates**: Check server logs for exceptions and bottlenecks

## Advanced Usage

To see all available variables in test plans that can be overridden, open the .jmx files in JMeter GUI and look at the User Defined Variables section. 