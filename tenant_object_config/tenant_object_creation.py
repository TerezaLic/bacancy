# Script reads configuraiton from a yaml file and generates SQL statements based on the configuration
# Snowflake role to be used : CALON_ADMIN which enabled db, warehouse, role creation

import yaml
import os

########## DEFINE ##############
def generate_sql_from_yaml(file_path):
    # Read the object_definition.yaml file
    with open(file_path, 'r') as file:
        object_definitions = yaml.safe_load(file)

    sql_statements = []
    # Generate the CREATE ..IF NOT EXISTS  statements

    # Generate the CREATE ..IF NOT EXISTS statements
    for snowflake_object in object_definitions['PROD']:
        # DATABASES
        if snowflake_object == 'DATABASE':
            for database in [object_definitions['PROD']['DATABASE']]:
                statement = f"CREATE DATABASE IF NOT EXISTS {database};"
                sql_statements.append(statement)
                #print(statement)
    
    for snowflake_object in object_definitions['DEV']:
        # DATABASES
        if snowflake_object == 'DATABASE':
            for database in [object_definitions['DEV']['DATABASE']]:
                statement = f"CREATE DATABASE IF NOT EXISTS {database};"
                sql_statements.append(statement)
                #print(statement)
            statement2= f"USE DATABASE {database};" 
            sql_statements.append(statement2)    

        # SCHEMAS        
        elif snowflake_object == 'SCHEMA':
            for schema in [object_definitions['DEV']['SCHEMA']]:
                statement = f"CREATE SCHEMA IF NOT EXISTS {schema};"
                sql_statements.append(statement)
                #print(statement)
               
        # WAREHOUSES        
        elif snowflake_object == 'WAREHOUSE':
            for warehouse in object_definitions['DEV']['WAREHOUSE']:
                warehouse_size = object_definitions['DEV']['WAREHOUSE'][warehouse]['SIZE']
                statement = f"CREATE WAREHOUSE IF NOT EXISTS {warehouse}\n  WAREHOUSE_SIZE = '{warehouse_size}';"
                sql_statements.append(statement)
                #print(statement)
               
        # ROLES
        elif snowflake_object == 'ROLE':
            for role in object_definitions['DEV']['ROLE']:
                statement = f"CREATE OR REPLACE ROLE {role};"
                sql_statements.append(statement)
                #print(statement)

                #role to be assinged to sysadmin
                statement2 = f"GRANT ROLE {role} TO ROLE SYSADMIN;"
                sql_statements.append(statement2)
                
                # Grant usage on databases
                for database in object_definitions['DEV']['ROLE'][role]['USE_DATABASES']:
                    statement = f"GRANT USAGE ON DATABASE {database} TO ROLE {role};"
                    sql_statements.append(statement)
                    #print(statement)
                    
                # Grant usage on schemas
                for schema in [object_definitions['DEV']['ROLE'][role]['USE_SCHEMA']]:
                    statement = f"GRANT USAGE ON SCHEMA {schema} TO ROLE {role};"
                    sql_statements.append(statement)
                    #print(statement)
                
                # Grant usage on warehouses
                for warehouse in [object_definitions['DEV']['ROLE'][role]['USE_WAREHOUSE']]:
                    statement = f"GRANT USAGE ON WAREHOUSE {warehouse} TO ROLE {role};"
                    sql_statements.append(statement)
                    #print(statement)
                
        # USERS             
        elif snowflake_object == 'USER':
            for user in object_definitions['DEV']['USER']:
                statement = f"CREATE USER IF NOT EXISTS {user} PASSWORD = 'password' DEFAULT_ROLE = {role} MUST_CHANGE_PASSWORD = TRUE;"
                sql_statements.append(statement)
                #print(statement)

                # Grant role to user
                for role in object_definitions['DEV']['ROLE']:
                    statement = f"GRANT ROLE {role} TO USER {user};"
                    sql_statements.append(statement)
                    #print(statement)

    return(sql_statements)


############## USE ##############

file_path = 'tenant_object_definition.yaml'
sql_statements = generate_sql_from_yaml(file_path)
print(sql_statements)



############## OUTPUT ##############
# RUN GENERATED SQL CODE ON SNOWFLKAE USING PYTHON
import snowflake.connector

# Set up the Snowflake connection parameters
conn_params = {
    'user': os.environ.get('SNOWFLAKE_USER'),
    'password': os.environ.get('SNOWFLAKE_PASSWORD'),
    'account': os.environ.get('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.environ.get('SNOWFLAKE_WAREHOUSE'),
    'role': os.environ.get('SNOWFLAKE_ROLE'),
}

print(conn_params)
# Create a connection to Snowflake
conn = snowflake.connector.connect(**conn_params)

# Create a cursor object to execute SQL statements
cursor = conn.cursor()

# Execute each SQL statement
for statement in sql_statements:
    cursor.execute(statement)

# Commit the changes
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()