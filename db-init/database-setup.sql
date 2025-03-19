-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tenants table for multi-tenant support
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain_name VARCHAR(255) NOT NULL UNIQUE,
    plan_tier VARCHAR(20) NOT NULL DEFAULT 'basic' CHECK (plan_tier IN ('basic', 'pro', 'enterprise')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table for authentication with tenant relationship
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tenant_id, email)
);

-- Goals table (top-level objectives)
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    target_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Initiatives table (mid-level projects)
CREATE TABLE initiatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'planned', 'completed')),
    priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    revenue DECIMAL(12,2),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'inactive', 'prospect')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ideas table
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    initiative_id UUID REFERENCES initiatives(id) ON DELETE SET NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('urgent', 'high', 'medium', 'low')),
    effort VARCHAR(5) NOT NULL CHECK (effort IN ('xs', 's', 'm', 'l', 'xl')),
    source VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('new', 'planned', 'completed', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Comments table for ideas, feedback, and initiatives
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    entity_type VARCHAR(20) NOT NULL CHECK (entity_type IN ('idea', 'feedback', 'initiative')),
    entity_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for Ideas and Customers (many-to-many)
CREATE TABLE ideas_customers (
    idea_id UUID REFERENCES ideas(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    PRIMARY KEY (idea_id, customer_id)
);

-- Junction table for Feedback and Customers (many-to-many)
CREATE TABLE feedback_customers (
    feedback_id UUID REFERENCES feedback(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    PRIMARY KEY (feedback_id, customer_id)
);

-- Junction table for Feedback and Initiatives (many-to-many)
CREATE TABLE feedback_initiatives (
    feedback_id UUID REFERENCES feedback(id) ON DELETE CASCADE,
    initiative_id UUID REFERENCES initiatives(id) ON DELETE CASCADE,
    PRIMARY KEY (feedback_id, initiative_id)
);

-- Add indexes for performance
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_goals_tenant_id ON goals(tenant_id);
CREATE INDEX idx_initiatives_tenant_id ON initiatives(tenant_id);
CREATE INDEX idx_initiatives_goal_id ON initiatives(goal_id);
CREATE INDEX idx_customers_tenant_id ON customers(tenant_id);
CREATE INDEX idx_ideas_tenant_id ON ideas(tenant_id);
CREATE INDEX idx_ideas_initiative_id ON ideas(initiative_id);
CREATE INDEX idx_feedback_tenant_id ON feedback(tenant_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_comments_entity ON comments(entity_type, entity_id);
CREATE INDEX idx_ideas_customers_idea_id ON ideas_customers(idea_id);
CREATE INDEX idx_ideas_customers_customer_id ON ideas_customers(customer_id);
CREATE INDEX idx_feedback_customers_feedback_id ON feedback_customers(feedback_id);
CREATE INDEX idx_feedback_customers_customer_id ON feedback_customers(customer_id);
CREATE INDEX idx_feedback_initiatives_feedback_id ON feedback_initiatives(feedback_id);
CREATE INDEX idx_feedback_initiatives_initiative_id ON feedback_initiatives(initiative_id);

-- Add triggers to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_goals_updated_at BEFORE UPDATE ON goals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_initiatives_updated_at BEFORE UPDATE ON initiatives FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ideas_updated_at BEFORE UPDATE ON ideas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_feedback_updated_at BEFORE UPDATE ON feedback FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add computed columns for customer stats (using views)
CREATE VIEW customer_stats AS
SELECT 
    c.id, 
    c.tenant_id,
    c.name,
    c.revenue,
    c.status,
    COUNT(DISTINCT ic.idea_id) AS idea_count,
    COUNT(DISTINCT fc.feedback_id) AS feedback_count
FROM 
    customers c
LEFT JOIN 
    ideas_customers ic ON c.id = ic.customer_id
LEFT JOIN 
    feedback_customers fc ON c.id = fc.customer_id
GROUP BY 
    c.id, c.tenant_id, c.name, c.revenue, c.status;