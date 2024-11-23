# Metric Metadata Service 
Welcome to the Metric Metadata Service!

[Brief description of the service and its purpose]

This FastAPI-based service is part of Matter's innovative mirco-service based platform.
Matter is a leading ESG (Environmental, Social, and Governance) analysis fintech company that provides innovative solutions to help investors and companies make informed decisions based on ESG factors. Our mission is to drive sustainable and responsible investment by leveraging cutting-edge technology and data-driven insights.

At Matter, we offer a comprehensive suite of tools and services, including:

- ESG data and ratings
- Portfolio analysis and optimization
- Company screening and benchmarking
- Customized reporting and analytics

Our team of experts combines deep domain knowledge in ESG with advanced data science and machine learning techniques to deliver actionable intelligence to our clients.

For more information about Matter, visit our website at [https://www.thisismatter.com/](https://www.thisismatter.com/).

---

# Introduction
[Provide a more detailed overview of the service, its functionality, and how it fits into the overall architecture of Matter's ESG analysis fintech ecosystem.]

[Remove when populating:

The template showcases two distinct demo workflows:

1. **Metrics** - Shows how cache is used for persistent storage, with Celery as a batching tool and asynchronous flow.
2. **Organizations** - Demonstrates the use of Databases via ORM.

In the near future, we aim to implement this logic in Cookie Cutter.
]

# Features
* [Feature 1]
* [Feature 2]
* [Feature 3]


# Getting started
Follow the instructions below to get started with the Metric Metadata Service.

## Installation

**Prerequisite:** Make sure that conda is installed.

Clone the repository:
```console
git clone git@github.com:Matter-Tech/metric-metadata-service.git
cd metric-metadata-service
```

**Linux**: Install Debian's ```libpq-dev``` package:
```console
sudo apt install libpq-dev
```

Setup a new conda environment (and specify the required Python version):
```console
conda create --name metric-metadata-service python=3.12
```

Activate the newly created environment:
```console
conda activate metric-metadata-service
```

Install Poetry:
```console
pip install poetry
```

Install the project's packages (including test libraries) with poetry:
```console
poetry install --with development
```

Set up `pre-commit` hooks specified in `.pre-commit-config.yaml` - right now formatting & linting with `ruff`:
```console
pip install pre-commit
pre-commit install
```


## Running

### Locally (with bash)

To start the application locally:

First, if you use WSL, find the WSL IP Address. This address can be later used to connect Postman to the API, and/or connect to other services e.g. database.
```console
# from WSL:

ip addr show eth0

# Look for the inet address, and it will typically be in the format 172.x.x.x or 192.x.x.x.
# Example:
# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
#    link/ether 00:15:5d:82:95:8d brd ff:ff:ff:ff:ff:ff
#    inet 172.25.90.23/20 brd 172.25.95.255 scope global eth0
#       valid_lft forever preferred_lft forever
#    inet6 fe80::215:5dff:fe82:958d/64 scope link
#       valid_lft forever preferred_lft forever
#
# In this case, the IP is 172.25.90.23
```

Load the environment variables in the following way:
```console
source ./scripts/load_env_var.sh
```

Run a docker-compose local environment, to enable the API to access essential services:

```console
./scripts/run_local_env.sh
```

Open another shell window.
Then launch the FastAPI App: 
```
cd src
python app/main.py
```

### Locally (with PyCharm)

Run a docker-compose local environment, enabling the API to access essential services:

```console
./scripts/run_local_env.sh
```

Open Pycharm. Then configure the project's interpreter to the conda environment you created in the first step.
When done, make sure to set the following in the Debug Configuration: 
1. Set the working path to the src folder.
2. Change from Script to Module and set to app.main
2. Point the env file to env/development.env

![Pycharm Debug Configuration](./images/pycharm.png)

### Containerized

A `docker-compose` is also provided, containing all the application dependencies, and can also be used for local development:
```
docker-compose up --build
```
Note: this setup could be used for end-to-end tests.
It may take up to 20 seconds for the service to be fully loaded.

## Testing

### Locally (with PyCharm)
First, run the test environment:
```console
./scripts/run_test_env.sh
```

Then run the tests with ```pytest```, or directly from **PyCharm**. 

### Containerized
The script below will run all the available tests in the following order:
1. Unit
2. Integration
3. End-to-End
```
./scripts/run_tests.sh
```
This script also creates and removes the test environment automatically.

## Database Migrations

To create a new database migration, create your BaseDBModel like this:

```python
class OrganizationModel(CustomBase):
    __tablename__ = "organizations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    organization_name = Column(String(100), unique=True, index=True, nullable=False)
    organization_email = Column(String(100), unique=True, index=True, nullable=False)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
```

Then run the following command to generate a new migration file:

```console
alembic revision --autogenerate --message "Create organization table"
```

This will create a new migration in the `alembic/versions` folder.

See docs here at: https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script

Then run the following to apply all the new migrations:

```console
alembic upgrade head
```

You can now run the following command to check the current state of the database:

```console
alembic heads --verbose
```

if you have multiple heads, run the command below to merge them. This will result in an empty migration that has multiple `down_versions`:

```console
alembic merge heads
```

Multiple heads are not supported by the deployment pipelines.

Migrations are automatically applied when running the application in kubernetes.
The relevant job `02_migrations_job.yaml` is in the `kubernetes` folder for each environment. 
When the container starts in kubernetes, it will wait for the migrations job to complete, before starting the application,
using the script `await_migrations.sh`.

# Deployment

This Metric Metadata Service repository comes with a built-in GitHub Actions CI/CD pipeline that automates the testing and deployment process. The pipeline is triggered whenever changes are pushed to the repository, ensuring that the code remains reliable and functional.

The CI/CD pipeline includes the following steps:

* **Testing:** The pipeline automatically runs the test suite associated with the API, executing unit tests, the integration, and the end-2-end tests to verify the correctness of the code. If any tests fail, the pipeline will halt, and the deployment will not proceed until the issues are resolved.
* **Containerization:** After successfully passing the tests, the pipeline builds a Docker image of the API using the provided Dockerfile. This image encapsulates the application code, dependencies, and runtime environment, making it easy to deploy and run consistently across different environments.
* **Deployment:** Once the Docker image is built, the pipeline can deploy the API to a target environment, such as a Kubernetes cluster. The repository includes Kubernetes YAML files located in the kubernetes folder, which define the necessary resources and configurations for deploying the API on a Kubernetes cluster.


# Business Logic

This section of the README.md should provide a detailed explanation of the business logic implemented in your Python FastAPI-based web service. It is essential to document and communicate the core functionality, rules, and processes that drive your application.

When writing this section, consider including the following aspects:

* **Purpose:** Clearly state the primary purpose and objectives of your web service. Explain how it solves specific business problems or addresses particular needs.
* **Workflow:** Describe the high-level workflow of your application. Outline the main steps involved in processing requests, handling data, and generating responses. Use diagrams or flowcharts if necessary to visualize the process.
* **Key Features:** Highlight the key features and functionalities of your web service. Explain how these features align with the business requirements and provide value to the users.
* **Data Models:** Document the primary data models used in your application. Describe the entities, their attributes, and the relationships between them. Clarify how these models represent the business domain and support the desired functionality.
* **Business Rules:** Specify any business rules, constraints, or validations applied within your application. Explain how these rules ensure data integrity, enforce business policies, and maintain the consistency of the system.
* **Integration Points:** If your web service integrates with external systems or APIs, document these integration points. Describe the purpose of each integration, the data exchanged, and any specific requirements or constraints.
* **Error Handling:** Explain how your application handles errors and exceptions. Describe the common error scenarios, the corresponding error codes or messages, and the appropriate actions taken in each case.
* **Logging and Monitoring:** Document your logging and monitoring strategy. Specify what information is logged, how it is captured, and where it is stored. Explain how this data can be used for troubleshooting, performance analysis, and business insights.
* **Assumptions and Limitations:** Clearly state any assumptions made during the development of your web service. Highlight any known limitations or constraints that users should be aware of when using your application.

Remember to keep your explanations clear, concise, and accessible to both technical and non-technical stakeholders. Use code snippets, examples, or references to specific files or modules to support your documentation when necessary.

By providing a comprehensive description of your application's business logic, you enable other developers, maintainers, and stakeholders to understand the core functionality and make informed decisions when working with your Python FastAPI-based web service.


# Project structure

The Metric Metadata Service project is organized into multiple layers, each responsible for specific functionality. This well-structured architecture promotes code separation, maintainability, and scalability. The project follows the three-layer architecture (router, service, and DAL) for handling API endpoints and business logic, along with an additional layer for async Celery tasks to enable asynchronous processing.

## Layers Description
### Router (Endpoints)
The api package contains the API routers that define the endpoints. Each router corresponds to a specific functionality, and the endpoints are defined using FastAPI's decorators. These routers handle incoming HTTP requests, validate the input data, and pass it to the appropriate service layer.

### Service (Business Logic)
The service package contains the business logic of the Metric Metadata Service. It contains modules responsible for processing incoming requests, performing ESG portfolio analysis, and returning analysis results. The service layer interacts with the Data Access Layer (DAL) to fetch data from the database or other external sources, as needed.

### DAL (Data Access Layer)
The dal package encapsulates the interaction with the database or any external data sources. It provides functions to perform CRUD operations and fetch data required for the analysis service. The DAL abstracts away the underlying data storage, making it easier to switch between different database implementations.

### Tasks (Async Celery)
The tasks package handles asynchronous Celery tasks. Celery is used for background processing to allow the API to perform certain tasks asynchronously. For example, long-running tasks such as complex analysis or third-party API interactions can be offloaded to Celery workers, freeing up the API to handle other incoming requests.

## Conclusion
The clear separation of concerns through the three-layer architecture (router, service, and DAL) ensures a well-organized and scalable codebase. The addition of async Celery tasks allows for efficient background processing, making the Metric Metadata Service responsive and performant even during resource-intensive operations.