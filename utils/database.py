import psycopg2
from psycopg2 import sql


class DatabaseUtil:

    def __init__(self, db_config):
        self.db_config = db_config
        try:
            self.connection = psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def schema_details(self, schema_name):
        schema_info_context = ""
        cursor = None
        schema_info_context = f"DataBase Schema Name: {schema_name}\n"

        if self.connection is None:
            return "Error: No active database connection."

        try:
            cursor = self.connection.cursor()

            # Get all tables in the schema
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = %s;",
                (schema_name,)
            )
            tables_list = cursor.fetchall() #  this is the function which converts result into the form of list

            for table in tables_list:
                table_name = table[0]
                schema_info_context += f"\nTable: {table_name}\n"

                # Columns and data types (filtered by schema AND table)
                cursor.execute(
                    """SELECT column_name, data_type 
                       FROM information_schema.columns 
                       WHERE table_schema = %s AND table_name = %s;""",
                    (schema_name, table_name)
                )
                columns_list = cursor.fetchall()

                for column_name, data_type in columns_list:
                    schema_info_context += f"  Column: {column_name}, Data Type: {data_type}\n"

                # Sample data (using safe identifiers, not raw f-string interpolation)
                query = sql.SQL("SELECT * FROM {}.{} LIMIT 5;").format(
                    sql.Identifier(schema_name),
                    sql.Identifier(table_name)
                )
                cursor.execute(query)
                sample_data = cursor.fetchall()

                schema_info_context += "  Sample Data:\n"
                for row in sample_data:
                    schema_info_context += f"    Row: {row}\n"

        except Exception as e:
            print(f"Error occurred while fetching schema details: {e}")
            schema_info_context = f"Error occurred while fetching schema details: {e}"

        finally:
            if cursor:
                cursor.close()
            if self.connection:
                self.connection.close()

        return schema_info_context

    def execute_query(self, query):
        cursor = None
        result = None

        if self.connection is None:
            return "Error: No active database connection."

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()  # Fetch all results by converting the result into a list
            self.connection.commit()  # Commit the transaction if needed

        except Exception as e:
            print(f"Error occurred while executing query: {e}")
            self.connection.rollback()
            result = f"Error occurred while executing query: {e}"

        finally:
            if cursor:
                cursor.close()
            if self.connection:
                self.connection.close()

        return str(result)  # Convert the result to string before returning