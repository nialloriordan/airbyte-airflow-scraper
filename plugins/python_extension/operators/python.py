from airflow.operators.python_operator import PythonOperator


class ExtendedPythonOperator(PythonOperator):
    """
    extending the python operator so macros
    get processed for the op_kwargs field.
    """

    template_fields = ("templates_dict", "op_kwargs")
