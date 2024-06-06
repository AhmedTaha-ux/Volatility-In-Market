import pandas as pd

class SQLRepository:
    def __init__(self, connection):
        self.connection = connection

    def insert_table(self, table_name, records, if_exists="fail"):
        """ To insert table in the database

        :param table_name: str
            name of table
        :param records: pd.DataFrame
            data will be inserted in database
        :param if_exists: str, optional
            How to behave if the table already exists. by dfault: 'fail'
            - 'fail': Raise a ValueError.
            - 'replace': Drop the table before inserting new values.
            - 'append': Insert new values to the existing table.
        :return: dict
             Dictionary has two keys:
            - 'transaction_successful', followed by bool
            - 'records_inserted', followed by int
        """
        n_inserted = records.to_sql(name=table_name, con=self.connection, if_exists=if_exists)

        return {
            'transaction_successful': True,
            'records_inserted': n_inserted
        }

    def read_table(self, table_name, limit=None):
        """ To read table from database.

        :param table_name: str
            Name of table in the database
        :param limit: int, by dfault None, optional
            Number of most recent records to retrieve. If `None`, all
            records are retrieved.
        :return: pd.DataFrame
            Index is DatetimeIndex "date". Columns are 'open', 'high',
            'low', 'close', and 'volume'. All columns are numeric.
        """
        # Create SQL query (with optional limit)
        if limit:
            sql = f"SELECT * FROM '{table_name}' LIMIT {limit}"
        else:
            sql = f"SELECT * FROM '{table_name}'"

        # Retrieve data, read into DataFrame
        df = pd.read_sql(sql=sql, con=self.connection, parse_dates=["date"], index_col="date")

        # Return DataFrame
        return df