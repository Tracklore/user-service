#!/bin/bash

# Create issues for user-service

# Function to create an issue
create_issue() {
    local title=$1
    local body=$2
    local labels=$3
    
    echo "Creating issue: $title"
    gh issue create --title "$title" --body "$body" --label "$labels"
}

# Function to create a label if it doesn't exist
create_label() {
    local label_name=$1
    local label_color=$2
    local label_desc=$3
    
    # Check if label exists
    if ! gh label list | grep -q "^$label_name"; then
        echo "Creating label: $label_name"
        gh label create "$label_name" --color "$label_color" --description "$label_desc"
    else
        echo "Label $label_name already exists"
    fi
}

# Create labels
create_label "security" "e11d21" "Security related issues"
create_label "enhancement" "a2eeef" "New feature or request"
create_label "database" "0052cc" "Database related issues"
create_label "configuration" "c5def5" "Configuration related issues"

# Create issues
create_issue "Standardize database connection management" "Implement consistent async database connection handling with proper connection pooling. Ensure database connections are properly managed and closed." "database,enhancement"
create_issue "Enhance security configuration" "Ensure all secret keys are properly configured via environment variables and not hardcoded. Implement secure secret management practices." "security,configuration"
create_issue "Implement comprehensive health checks" "Add detailed health checks that verify database connectivity and other dependencies. Include checks for message queue connectivity." "monitoring,enhancement"

echo "All issues created for user-service!"