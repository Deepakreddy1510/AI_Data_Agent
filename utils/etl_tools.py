import os 
import requests
import pandas as pd

class ETLTools:

    def __init__(self):
        pass

    def extract_load(self,url:str, output_folder:str, format:str):
        """
        This tool extracts the data from the API (url) and loads it into the
        the desired location (output_folder).

        Args:
            url (str): The API endpoint from which to extract the data.
            output_folder (str): The folder where the extracted data will be saved.

        Returns:
            str: A message indicating the success or failure of the operation.


        """
        
        # We need to set the project root because i want to write the data in data folder
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        output_folder = os.path.join(project_root, output_folder)

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json() # Convert the data which is in string format to JSON

            filename = os.path.join(output_folder, f"extracted_data.{format}")
            os.makedirs(output_folder, exist_ok= True)
            
            # We want to fetch name, url so we used data['results'] to fetch the data\
            # Check in extracted_data.json file to understand the data structure
            df = pd.json_normalize(data['results'])
            if format == "csv":
                df.to_csv(filename, index=False)
            elif format == "json":
                df.to_json( filename, orient="records", lines=True)
            elif format == "parquet":
                df.to_json(filename, orient="records", lines=True)
            else:
                return f"Unsupported format: {format}"
            
            return f"Data successfully extracted and saved to {filename}"
        except requests.exceptions.RequestException as e:
            return f"Failed to extract data: {e}"
    
    def transform_load_context(self, file_path:str, output_folder:str, output_format:str):
        """
        This tool transforms the data from the specified file and loads it into the desired location (output_folder).

        Args:
            file_path (str): The path to the file containing the data to be transformed.
            output_folder(str): The folder where the transformed data will be saved. 

        Returns:
            str: A message indicating the success or failure of the operation.
        """

        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".csv":
            df = pd.read_csv(file_path)
        elif file_extension == ".json":
            df = pd.read_json(file_path)
        elif file_extension == ".parquet":
            df = pd.read_parquet(file_path)
        else:
            return f"Unsupported file extension: {file_extension}"

        # We want to fetch the top 3 rows of the data and we want to return it in a string format because
        # we are using it in the context of the agent
        top_3_rows = str(df.head(3))

        return top_3_rows


if __name__ == "__main__":
    # This is the main function that will be used to extract the data from the API and save it to the CSV file
    obj = ETLTools()
    print(obj.extract_load("https://pokeapi.co/api/v2/pokemon/", "data/extract", "csv"))


