Echo - Product Alignment & Feedback Management Platform
-------------------------------------------------------

Echo is a multi-tenant software application designed to align business goals with product initiatives and customer feedback. It creates a hierarchical structure that connects high-level business objectives to granular customer input, helping organizations make data-driven product decisions.

### Core Purpose

Echo streamlines prioritization by connecting high-level business goals to specific customer feedback through a clear hierarchy, enabling teams to make informed decisions about product development.

### Key Components

1.  Goals - High-level business objectives (ideally 3-5) with titles, descriptions, and target dates. These represent the strategic direction of the company.
2.  Initiatives - Mid-level projects that support specific goals. Each has a title, description, status (active, planned, or completed), and priority. Initiatives bridge the gap between abstract business goals and concrete product features.
3.  Ideas - Specific suggestions from various sources (business team, product team, or customers). Each idea includes a title, description, priority (urgent, high, medium, low), effort estimation (xs, s, m, l, xl), source, and status (new, planned, completed, or rejected).
4.  Feedback - Input from customers or teams with sentiment tracking (positive, neutral, negative). Feedback can be linked to initiatives and specific customers.
5.  Customers - Organizations or individuals who provide ideas and feedback. Customer profiles include revenue information, status (active, inactive, prospect), and automatically calculated statistics on their contributions.
6.  Comments - Discussion threads attached to ideas, feedback, and initiatives to facilitate collaboration.

### Technical Architecture

1.  Multi-tenant Design - Organizations have isolated data environments with their own users, goals, initiatives, ideas, feedback, and customers.
2.  User Roles - Supports different permission levels (admin, business, product) for various team members.
3.  Flask Backend - Python-based web framework with blueprint organization for modularity.
4.  PostgreSQL Database - Relational database with well-defined relationships between entities.
5.  Authentication - JWT-based authentication system with tenant isolation middleware.

### Key Relationships

-   Goals contain multiple Initiatives
-   Initiatives contain multiple Ideas
-   Ideas can be associated with multiple Customers
-   Feedback can be linked to multiple Initiatives
-   Feedback can come from multiple Customers
-   Users can create Comments on Ideas, Feedback, and Initiatives

### Business Value

1.  Strategic Alignment - Ensures all product work ties directly to business objectives
2.  Customer-Centric - Prioritizes based on real customer needs and feedback
3.  Data-Driven - Provides quantifiable metrics to inform decision making
4.  Transparency - Creates visibility between business, product, and customer needs
5.  Collaboration - Enables discussion through comments and shared visibility

In summary, Echo serves as a centralized platform where business strategy, product planning, and customer input converge to create a coherent product development process that's both strategic and responsive to market needs.
* * * * *


## Steps to run:
1 Create a `.env` file in your project root and add the following variables:

`#Database Configuration`
`POSTGRES_USER=`
`POSTGRES_PASSWORD=`
`POSTGRES_DB=`
`DATABASE_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_DB}?sslmode=disable`

`#Security Keys`
`FLASK_SECRET_KEY=`
`JWT_SECRET_KEY=`

`#Ports & Gunicorn Configuration`
`WEB_PORT=5005`
`DB_PORT=5435`
`GUNICORN_BIND=0.0.0.0:5435`
`GUNICORN_WORKERS=4`

`#Flask Settings`
`FLASK_APP=run.py`
`PYTHONUNBUFFERED=1`
`FLASK_ENV=development or production`
`FLASK_DEBUG=1 or 0`

* * * * *

### **2 Upgrade Dependencies**

Ensure you're using the latest package versions:

`pip3 install --upgrade pip`
`pip3 install --upgrade -r requirements.txt`

* * * * *

### **3 Set Up Your Dockerized Flask + PostgreSQL Environment**

`docker-compose down        # Stop and remove containers`
`docker-compose build       # Rebuild the images`
`docker-compose up -d       # Start containers in detached mode`

* * * * *

### **4 Access the Database**

To enter the running **PostgreSQL container** and interact with the database:

`docker ps  # Get container ID`
`docker exec -it <container_id> psql -U admin -d echo_db`


* * * * *

### **5 Validate on Localhost**

Once everything is running, visit:\
  **http://localhost:5005** *(or the port set in `.env`)*